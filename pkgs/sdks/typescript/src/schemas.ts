import { ConditionOperator, EntityType, PolicyEffect } from "./enums";

/**
 * Represents an attribute with key-value pair
 */
export interface Attribute {
  key: string;
  value: string;
}

/**
 * Represents an attribute as stored in the database
 */
export interface AttributeInDb extends Attribute {
  updated_at: string; // ISO datetime
  registered_at: string; // ISO datetime
}

/**
 * Base interface for all entity types
 */
export interface EntityBase {
  uri?: string;
  type: EntityType;
  attributes: Record<string, string>;
}

/**
 * Request body for creating a new entity
 */
export interface EntityCreate extends EntityBase { }

/**
 * Request body for updating an existing entity
 */
export interface EntityUpdate {
  uri: string;
  attributes: Record<string, string>;
}

/**
 * Response from the server when an entity is created or updated
 */
export interface EntityInDb {
  uri: string;
  type: EntityType;
  attributes: AttributeInDb[];
  registered_at: string; // ISO datetime
}

/**
 * Base interface for access control entities
 */
export interface EntityAccess {
  uri?: string;
  attributes: Record<string, string>;
  type: EntityType;
}

/**
 * Resource in an access control request
 */
export interface ResourceAccess extends EntityAccess {
  type: EntityType.Resource;
}

/**
 * Principal in an access control request
 */
export interface PrincipalAccess extends EntityAccess {
  type: EntityType.Principal;
}

/**
 * Complete access request to check permissions
 */
export interface AccessRequest {
  principal: PrincipalAccess;
  resource: ResourceAccess;
  action?: "access";
}

/**
 * Represents a condition for policy evaluation
 */
export interface Condition {
  path: string;
  operator: ConditionOperator;
  value: string;
}

/**
 * Represents a rule in a policy
 */
export interface Rule {
  effect: PolicyEffect;
  principal_conditions: Condition[];
  resource_conditions: Condition[];
  actions: string[];
}

/**
 * Represents a policy with a list of access rules
 */
export interface Policy {
  name: string;
  description?: string;
  rules: Rule[];
  default_effect: PolicyEffect;
}

/**
 * Represents the result of a policy evaluation
 */
export interface PolicyEvaluationResult {
  effect: PolicyEffect;
  matched_rule?: Rule;
  policy_name: string;
}
