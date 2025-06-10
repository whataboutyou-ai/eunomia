/**
 * Enum representing the types of entities in the system.
 */
export enum EntityType {
  Resource = "resource",
  Principal = "principal",
}

/**
 * Enum representing the effect of a policy rule.
 */
export enum PolicyEffect {
  Allow = "allow",
  Deny = "deny",
}

/**
 * Enum representing condition operators for policy rules.
 */
export enum ConditionOperator {
  Equals = "equals",
  NotEquals = "not_equals",
  // String operators
  Contains = "contains",
  NotContains = "not_contains",
  StartsWith = "startswith",
  EndsWith = "endswith",
  // Number operators
  Greater = "gt",
  GreaterOrEqual = "gte",
  Less = "lt",
  LessOrEqual = "lte",
  // List operators
  In = "in",
  NotIn = "not_in",
}
