import axios from "axios";
import { EunomiaClient, EntityType } from "../index";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe("EunomiaClient", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedAxios.create.mockReturnValue(mockedAxios as any);
  });

  describe("constructor", () => {
    it("should use default values when no options are provided", () => {
      const client = new EunomiaClient();
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: "http://localhost:8000",
        headers: {},
        timeout: 60000,
      });
    });

    it("should use provided values when options are specified", () => {
      const client = new EunomiaClient({
        serverHost: "https://example.com",
        apiKey: "test-api-key",
      });
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: "https://example.com",
        headers: {
          "WAY-API-KEY": "test-api-key",
        },
        timeout: 60000,
      });
    });
  });

  describe("checkAccess", () => {
    it("should make correct API call and return the result", async () => {
      mockedAxios.post.mockResolvedValueOnce({ data: true });

      const client = new EunomiaClient();
      const result = await client.checkAccess({
        principalUri: "user:123",
        resourceUri: "resource:456",
        principalAttributes: { role: "admin" },
        resourceAttributes: { type: "document" },
      });

      expect(mockedAxios.post).toHaveBeenCalledWith("/check-access", {
        principal: {
          uri: "user:123",
          attributes: { role: "admin" },
          type: EntityType.Principal,
        },
        resource: {
          uri: "resource:456",
          attributes: { type: "document" },
          type: EntityType.Resource,
        },
      });
      expect(result).toBe(true);
    });
  });

  describe("registerEntity", () => {
    it("should make correct API call and return the created entity", async () => {
      const mockEntity = {
        uri: "resource:123",
        type: EntityType.Resource,
        attributes: [],
        registered_at: "2023-01-01T00:00:00Z",
      };
      mockedAxios.post.mockResolvedValueOnce({ data: mockEntity });

      const client = new EunomiaClient();
      const result = await client.registerEntity({
        type: EntityType.Resource,
        attributes: { name: "Test Resource" },
        uri: "resource:123",
      });

      expect(mockedAxios.post).toHaveBeenCalledWith("/register-entity", {
        type: EntityType.Resource,
        attributes: { name: "Test Resource" },
        uri: "resource:123",
      });
      expect(result).toEqual(mockEntity);
    });
  });
});
