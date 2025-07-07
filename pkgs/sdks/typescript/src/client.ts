import axios, { AxiosInstance, AxiosResponse } from "axios";
import {
  CheckRequest,
  CheckResponse,
  EntityCreate,
  EntityInDb,
  EntityType,
  EntityUpdate,
  Policy,
} from "./index";

/**
 * Options for configuring the EunomiaClient
 */
export interface EunomiaClientOptions {
  endpoint?: string;
  apiKey?: string;
}

/**
 * A client for interacting with the Eunomia server.
 *
 * This client provides methods to register resources and principals,
 * and to check permissions.
 */
export class EunomiaClient {
  private readonly endpoint: string;
  private readonly apiKey: string | undefined;
  public readonly client: AxiosInstance;

  /**
   * Creates a new EunomiaClient instance.
   *
   * @param options - Configuration options for the client
   * @param options.endpoint - The base URL endpoint of the Eunomia server (defaults to "http://localhost:8000")
   * @param options.apiKey - The API key for authenticating with the server (defaults to process.env.WAY_API_KEY)
   */
  constructor(options: EunomiaClientOptions = {}) {
    this.endpoint = options.endpoint || "http://localhost:8000";
    this.apiKey = options.apiKey || process.env.WAY_API_KEY;

    const headers: Record<string, string> = {};
    if (this.apiKey) {
      headers["WAY-API-KEY"] = this.apiKey;
    }

    this.client = axios.create({
      baseURL: this.endpoint,
      headers,
      timeout: 60000,
    });
  }

  /**
   * Handles the response from the Eunomia server, throwing errors for non-success status codes.
   *
   * @param response - The axios response to handle
   * @returns The response data
   * @throws Error if the response status is not in the 2xx range
   */
  private handleResponse<T>(response: AxiosResponse<T>): T {
    return response.data;
  }

  /**
   * Check whether a principal has permissions to perform an action on a specific resource.
   *
   * @param options - Options for the check request
   * @param options.principalUri - The identifier of the principal (optional)
   * @param options.resourceUri - The identifier of the resource (optional)
   * @param options.principalAttributes - The attributes of the principal (optional)
   * @param options.resourceAttributes - The attributes of the resource (optional)
   * @param options.action - The action to check permissions for (optional, defaults to "access")
   * @returns A promise that resolves to true if the request is allowed, false otherwise
   */
  async check(options: {
    principalUri?: string;
    resourceUri?: string;
    principalAttributes?: Record<string, string>;
    resourceAttributes?: Record<string, string>;
    action?: string;
  }): Promise<CheckResponse> {
    const request: CheckRequest = {
      principal: {
        uri: options.principalUri,
        attributes: options.principalAttributes || {},
        type: EntityType.Principal,
      },
      resource: {
        uri: options.resourceUri,
        attributes: options.resourceAttributes || {},
        type: EntityType.Resource,
      },
      action: options.action || "access",
    };

    try {
      const response = await this.client.post<CheckResponse>(
        "/check",
        request,
      );
      return this.handleResponse(response);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP ${error.response.status}: ${error.response.data}`,
        );
      }
      throw error;
    }
  }

  /**
   * Perform a set of permission checks in a single request.
   *
   * @param checkRequests - The list of check requests to perform
   * @returns A promise that resolves to the list of results of the check requests
   */
  async bulkCheck(checkRequests: CheckRequest[]): Promise<CheckResponse[]> {
    try {
      const response = await this.client.post<CheckResponse[]>(
        "/check/bulk",
        checkRequests,
      );
      return this.handleResponse(response);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP ${error.response.status}: ${error.response.data}`,
        );
      }
      throw error;
    }
  }

  /**
   * Register a new entity with the Eunomia server.
   *
   * @param options - Options for registering the entity
   * @param options.type - The type of entity to register
   * @param options.attributes - The attributes to associate with the entity
   * @param options.uri - The URI for the entity (optional)
   * @returns A promise that resolves to the newly registered entity
   */
  async registerEntity(options: {
    type: EntityType;
    attributes: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
    uri?: string;
  }): Promise<EntityInDb> {
    const entity: EntityCreate = {
      type: options.type,
      attributes: options.attributes,
      uri: options.uri,
    };

    try {
      const response = await this.client.post<EntityInDb>(
        "/admin/fetchers/registry/entities",
        entity,
      );
      return this.handleResponse(response);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP ${error.response.status}: ${error.response.data}`,
        );
      }
      throw error;
    }
  }

  /**
   * Update the attributes of an existing entity.
   *
   * @param options - Options for updating the entity
   * @param options.uri - The URI of the entity to update
   * @param options.attributes - The attributes to update
   * @param options.override - If true, replace existing attributes; if false, merge them (default: false)
   * @returns A promise that resolves to the updated entity
   */
  async updateEntity(options: {
    uri: string;
    attributes: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
    override?: boolean;
  }): Promise<EntityInDb> {
    const entity: EntityUpdate = {
      uri: options.uri,
      attributes: options.attributes,
    };

    try {
      const response = await this.client.put<EntityInDb>(
        `/admin/fetchers/registry/entities/${options.uri}`,
        entity,
        {
          params: { override: options.override || false },
        },
      );
      return this.handleResponse(response);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP ${error.response.status}: ${error.response.data}`,
        );
      }
      throw error;
    }
  }

  /**
   * Delete an entity from the Eunomia server.
   *
   * @param uri - The URI of the entity to delete
   * @returns A promise that resolves when the entity is deleted
   */
  async deleteEntity(uri: string): Promise<boolean> {
    try {
      const response = await this.client.delete(
        `/admin/fetchers/registry/entities/${uri}`,
      );
      return this.handleResponse(response);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP ${error.response.status}: ${error.response.data}`,
        );
      }
      throw error;
    }
  }

  /**
   * Create a new policy and store it in the Eunomia server.
   *
   * @param policy - The policy to create
   * @returns A promise that resolves to the created policy
   */
  async createPolicy(policy: Policy): Promise<Policy> {
    try {
      const response = await this.client.post<Policy>(
        "/admin/policies",
        policy,
      );
      return this.handleResponse(response);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP ${error.response.status}: ${error.response.data}`,
        );
      }
      throw error;
    }
  }

  /**
   * Create a new simple policy with a single rule and store it in the Eunomia server.
   *
   * @param request - The check request to create the policy from
   * @param name - The name of the policy
   * @returns A promise that resolves to the created policy
   */
  async createSimplePolicy(request: CheckRequest, name: string): Promise<Policy> {
    try {
      const response = await this.client.post<Policy>(
        "/admin/policies/simple",
        request,
        {
          params: { name },
        },
      );
      return this.handleResponse(response);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP ${error.response.status}: ${error.response.data}`,
        );
      }
      throw error;
    }
  }

  /**
   * Get all policies from the Eunomia server.
   *
   * @returns A promise that resolves to the list of all policies
   */
  async getPolicies(): Promise<Policy[]> {
    try {
      const response = await this.client.get<Policy[]>("/admin/policies");
      return this.handleResponse(response);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP ${error.response.status}: ${error.response.data}`,
        );
      }
      throw error;
    }
  }

  /**
   * Delete a policy from the Eunomia server.
   *
   * @param name - The name of the policy to delete
   * @returns A promise that resolves to true if the policy was successfully deleted
   */
  async deletePolicy(name: string): Promise<boolean> {
    try {
      const response = await this.client.delete<boolean>(`/admin/policies/${name}`);
      return this.handleResponse(response);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP ${error.response.status}: ${error.response.data}`,
        );
      }
      throw error;
    }
  }
}
