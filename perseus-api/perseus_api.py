from peewee import ProgrammingError
from app import app
from utils.constants import GENERATE_CDM_XML_ARCHIVE_PATH, \
    GENERATE_CDM_XML_ARCHIVE_FILENAME, GENERATE_CDM_XML_ARCHIVE_FORMAT
from flask import request, jsonify, send_from_directory
from services.xml_writer import get_xml, zip_xml, \
    delete_generated_xml, get_lookups_list, get_lookup, add_lookup, del_lookup
from services.source_schema import load_schema_to_server, \
    load_saved_source_schema_from_server, save_source_schema_in_db, get_view_from_db, run_sql_transformation, \
    get_column_info, get_field_type
from services.cdm_schema import get_exist_version, get_schema
from utils.exceptions import InvalidUsage
import traceback
from werkzeug.exceptions import BadRequestKeyError
from flask import Blueprint
from config import VERSION, APP_PREFIX
from utils.utils import username_header

perseus = Blueprint('perseus', __name__, url_prefix=APP_PREFIX)


@perseus.route('/api/info', methods=['GET'])
def get_app_version():
    app.logger.info("REST request to GET app info")
    return jsonify({'name': 'Perseus', 'version': VERSION})


@perseus.route('/api/load_schema', methods=['GET', 'POST'])
@username_header
def load_schema(current_user):
    """save source schema to server side"""
    app.logger.info("REST request to load schema")
    try:
        if request.method == 'POST':
            file = request.files['file']
            load_schema_to_server(file, current_user)
    except InvalidUsage as e:
        raise e
    except Exception as error:
        raise InvalidUsage(error.__str__(), 500)
    return jsonify(success=True)


@perseus.route('/api/load_saved_source_schema', methods=['GET'])
@username_header
def load_saved_source_schema_call(current_user):
    """load saved source schema by name"""
    app.logger.info("REST request to load saved source schema")
    try:
        schema_name = request.args['schema_name']
        saved_schema = load_saved_source_schema_from_server(current_user, schema_name)
    except InvalidUsage as e:
        raise e
    except Exception as error:
        raise InvalidUsage(error.__str__(), 500)
    return jsonify([s.to_json() for s in saved_schema])


@perseus.route(f'/api/save_and_load_schema', methods=['GET', 'POST'])
@username_header
def save_and_load_schema_call(current_user):
    """save schema to server and load it from server in the same request"""
    app.logger.info("REST request to save and load schema")
    try:
        delete_generated_xml(current_user)
        if request.method == 'POST':
            file = request.files['file']
            load_schema_to_server(file, current_user)
        saved_schema = load_saved_source_schema_from_server(current_user, file.filename)
    except InvalidUsage as error:
        raise error
    except Exception as error:
        raise InvalidUsage(error.__str__(), 500)
    return jsonify([s.to_json() for s in saved_schema])


@perseus.route(f'/api/load_schema_to_server', methods=['POST'])
@username_header
def load_schema_call(current_user):
    """save schema to server and load it from server in the same request"""
    app.logger.info("REST request to load schema to server")
    try:
        file = request.files['file']
        load_schema_to_server(file, current_user)
    except Exception as error:
        raise InvalidUsage('Schema was not loaded', 500)
    return jsonify('OK')


@perseus.route('/api/save_source_schema_to_db', methods=['POST'])
@username_header
def save_source_schema_to_db_call(current_user):
    app.logger.info("REST request to save source schema to db")
    try:
        source_tables = request.json
        save_source_schema_in_db(current_user, source_tables)
    except Exception as error:
        raise InvalidUsage(error.__str__(), 500)
    return jsonify('OK')


@perseus.route('/api/get_view', methods=['POST'])
@username_header
def get_View(current_user):
    app.logger.info("REST request to get view")
    try:
        view_sql = request.get_json()
        view_result = get_view_from_db(current_user, view_sql['sql'])
    except ProgrammingError as error:
        raise InvalidUsage(error.__str__(), 400)
    except Exception as error:
        raise InvalidUsage(error.__str__(), 500)
    return jsonify(view_result)


@perseus.route('/api/validate_sql', methods=['POST'])
@username_header
def validate_Sql(current_user):
    app.logger.info("REST request to validate sql")
    try:
        sql_transformation = request.get_json()
        sql_result = run_sql_transformation(current_user, sql_transformation['sql'])
    except ProgrammingError as error:
        raise InvalidUsage(error.__str__(), 400)
    except Exception as error:
        raise InvalidUsage(error.__str__(), 500)
    return jsonify(sql_result)


@perseus.route('/api/get_cdm_versions')
@username_header
def get_cdm_versions_call(current_user):
    """return available CDM versions schema list"""
    app.logger.info("REST request to get CDM versions")
    return jsonify(get_exist_version())


@perseus.route('/api/get_cdm_schema')
@username_header
def get_cdm_schema_call(current_user):
    """return CDM schema for target version"""
    app.logger.info("REST request to get CDM schema")
    cdm_version = request.args['cdm_version']
    cdm_schema = get_schema(cdm_version)
    return jsonify([s.to_json() for s in cdm_schema])


@perseus.route('/api/get_column_info')
@username_header
def get_column_info_call(current_user):
    """return top 10 values by freq for table and row(optionally)
    based on WR report
    """
    app.logger.info("REST request to get column info")
    try:
        table_name = request.args['table_name']
        column_name = request.args.get('column_name')
        report_name = request.args.get('report_name')
        info = get_column_info(current_user, report_name, table_name, column_name);
    except InvalidUsage as error:
        raise InvalidUsage('Info cannot be loaded due to not standard structure of report', 400)
    except FileNotFoundError as error:
        raise InvalidUsage('Report not found', 404)
    except Exception as e:
        raise InvalidUsage(e.__str__(), 500)
    return jsonify(info)


@perseus.route('/api/get_xml', methods=['POST'])
@username_header
def xml(current_user):
    """return XML for CDM builder in map {source_table: XML, } and
    create file on back-end
    """
    app.logger.info("REST request to get XML")
    json = request.get_json()
    xml_ = get_xml(current_user, json)
    return jsonify(xml_)


@perseus.route('/api/get_zip_xml')
@username_header
def zip_xml_call(current_user):
    """return attached ZIP of XML's from back-end folder
    TODO  - now the folder is not cleared
    """
    app.logger.info("REST request to get zip XML")
    try:
        zip_xml(current_user)
    except Exception as error:
        raise InvalidUsage(error.__str__(), 404)
    return send_from_directory(
        directory=f"{GENERATE_CDM_XML_ARCHIVE_PATH}/{current_user}",
        path='.'.join((GENERATE_CDM_XML_ARCHIVE_FILENAME, GENERATE_CDM_XML_ARCHIVE_FORMAT)),
        as_attachment=True
    )


@perseus.route('/api/get_lookup')
@username_header
def get_lookup_by_name(current_user):
    app.logger.info("REST request to get lookup")
    name = request.args['name']
    lookup_type = request.args['lookupType']
    lookup = get_lookup(current_user, name, lookup_type)
    return jsonify(lookup)


@perseus.route('/api/get_lookups_list')
@username_header
def get_lookups(current_user):
    app.logger.info("REST request to get lookup list")
    lookup_type = request.args['lookupType']
    lookups_list = get_lookups_list(current_user, lookup_type)
    return jsonify(lookups_list)


@perseus.route('/api/save_lookup', methods=['POST'])
@username_header
def save_lookup(current_user):
    app.logger.info("REST request to save lookup")
    try:
        lookup = request.json
        add_lookup(current_user, lookup)
    except Exception as error:
        raise InvalidUsage(error.__str__(), 500)
    return jsonify(success=True)


@perseus.route('/api/delete_lookup', methods=['DELETE'])
@username_header
def delete_lookup(current_user):
    app.logger.info("REST request to delete lookup")
    try:
        name = request.args['name']
        lookup_type = request.args['lookupType']
        del_lookup(current_user, name, 'source_to_standard')
        del_lookup(current_user, name, 'source_to_source')
    except Exception as error:
        raise InvalidUsage(error.__str__(), 500)
    return jsonify(success=True)


@perseus.route('/api/get_user_schema_name', methods=['GET'])
@username_header
def get_schema_name(current_user):
    app.logger.info("REST request to get user schema name")
    return jsonify(current_user)


@perseus.route('/api/get_field_type', methods=['GET'])
@username_header
def get_field_type_call(current_user):
    app.logger.info("REST request to get field type")
    type = request.args['type']
    result_type = get_field_type(type)
    return jsonify(result_type)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """handle error of wrong usage on functions"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    traceback.print_tb(error.__traceback__)
    return response


@app.errorhandler(BadRequestKeyError)
def handle_bad_request_key(error):
    """handle error of missed/wrong parameter"""
    response = jsonify({'message': error.__str__()})
    response.status_code = 400
    traceback.print_tb(error.__traceback__)
    return response


@app.errorhandler(KeyError)
def handle_invalid_req_key(error):
    """handle error of missed/wrong parameter"""
    response = jsonify({'message': f'{error.__str__()} missing'})
    response.status_code = 400
    traceback.print_tb(error.__traceback__)
    return response


@app.errorhandler(Exception)
def handle_excpetion(error):
    """handle error of missed/wrong parameter"""
    response = jsonify({'message': error.__str__()})
    response.status_code = 500
    traceback.print_tb(error.__traceback__)
    return response
