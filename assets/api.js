export default async function executeCommand(serverUrl, command, username, password) {
  const authHeader = `Basic ${btoa(`${username}:${password}`)}`;
  const requestBody = { "command": command };
  const response = await fetch(`${serverUrl}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' ,
               'Authorization': authHeader,
            },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to execute command: ${error}`);
  }

  const result = await response.json();
  return { code: result.code, output: result.output, error: result.error };
}