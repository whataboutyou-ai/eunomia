/* eslint-disable @typescript-eslint/no-explicit-any */
import { ConditionOperator, EntityType, PolicyEffect } from "./enums";

/**
 * Represents an attribute with key-value pair
 */
export interface Attribute {
  key: string;
  value: any;
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
  uri: string;
  attributes: Record<string, any>;
  type: EntityType;
}

/**
 * Request body for creating a new entity
 */
export interface EntityCreate extends Omit<EntityBase, "uri"> {
  uri?: string;
}

/**
 * Request body for updating an existing entity
 */
export interface EntityUpdate extends Omit<EntityBase, "type"> {
  type?: EntityType;
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
 * Base interface for check request entities
 */
export interface EntityCheck {
  uri?: string;
  attributes?: Record<string, any>;
  type: EntityType;
}

/**
 * Resource in a check request
 */
export interface ResourceCheck extends EntityCheck {
  type: EntityType.Resource;
}

/**
 * Principal in a check request
 */
export interface PrincipalCheck extends EntityCheck {
  type: EntityType.Principal;
}

/**
 * Complete request to check permissions
 */
export interface CheckRequest {
  principal: PrincipalCheck;
  resource: ResourceCheck;
  action: string;
}

/**
 * Response from the server when a check request is made
 */
export interface CheckResponse {
  allowed: boolean;
  reason?: string;
}

/**
 * Represents a condition for policy evaluation
 */
export interface Condition {
  path: string;
  operator: ConditionOperator;
  value: any;
}

/**
 * Represents a rule in a policy
 */
export interface Rule {
  name: string;
  effect: PolicyEffect;
  principal_conditions: Condition[];
  resource_conditions: Condition[];
  actions: string[];
}

/**
 * Represents a policy with a list of rules
 */
export interface Policy {
  version: string;
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
