import { test, expect } from "@playwright/test";

test("page renders", async ({ page, baseURL }) => {
  console.log("baseURL:", baseURL);
  await page.goto(baseURL!);
  await expect(page.locator("body")).toContainText("File Upload Demo");
});
