const tseslint = require("@typescript-eslint/eslint-plugin");
const tseslintParser = require("@typescript-eslint/parser");

module.exports = [
  {
    ignores: ["node_modules/**", "dist/**"],
  },
  {
    files: ["**/*.ts"],
    languageOptions: {
      parser: tseslintParser,
      parserOptions: {
        project: ["./tsconfig.json", "./examples/tsconfig.json"],
        ecmaVersion: "latest",
        sourceType: "module",
      },
    },
    plugins: {
      "@typescript-eslint": tseslint,
    },
    rules: {
      // TypeScript specific rules
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/explicit-function-return-type": "warn",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],

      // General best practices
      "no-console": ["warn", { allow: ["warn", "error"] }],
      "no-return-await": "error",
      "prefer-const": "error",
      eqeqeq: ["error", "always", { null: "ignore" }],

      // Style
      semi: ["error", "always"],
      quotes: ["error", "double", { avoidEscape: true }],
      indent: ["error", 2],
      "comma-dangle": ["error", "always-multiline"],
    },
  },
];
