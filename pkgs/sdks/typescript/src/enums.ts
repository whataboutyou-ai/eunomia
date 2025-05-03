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
  In = "in",
  NotIn = "not_in",
  Contains = "contains",
  NotContains = "not_contains",
  StartsWith = "starts_with",
  EndsWith = "ends_with",
  Greater = "greater",
  GreaterOrEqual = "greater_or_equal",
  Less = "less",
  LessOrEqual = "less_or_equal",
  Exists = "exists",
  NotExists = "not_exists",
}
