import { SqlFunctionForTransformationState } from '@models/transformation/sql-function-for-transformation';

export interface SqlForTransformation {
  applied?: boolean
  name?: string // For Manual sql
  functions?: SqlFunctionForTransformationState[] // For Visual sql
}
