import reactPlugin from "eslint-plugin-react";
export default [
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: { ecmaVersion: 2022, sourceType: "module" },
    plugins: { react: reactPlugin },
    rules: { "react/jsx-key": "error" },
  },
];
