import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

const server = new McpServer({
  name: "custom-github-skills",
  version: "1.0.0"
});

// Define your tools here
server.tool("get_skill_info", {}, async () => {
  return { content: [{ type: "text", text: "Skill executed successfully!" }] };
});
