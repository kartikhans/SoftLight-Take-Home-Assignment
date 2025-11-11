# AI Browser Agent for UI State Capture

This project is an AI-powered browser agent designed to autonomously navigate web applications and capture UI states, 
even for actions that don't have unique URLs.

Given a high-level task (e.g., "Add two todos: 'Buy milk' and 'Wash car', then delete 'Call mom'"), the agent uses 
a large language model (LLM) to "think" step-by-step, controlling a live browser to execute the task while saving a 
screenshot at every stage.

This system was built to solve the challenge of capturing "non-URL states" (like modals, form inputs, or dynamic UI 
changes) for multi-step workflows.

# How It Works: The Perception-Decision-Action Loop 🚀

The agent operates on a continuous Perception-Decision-Action loop, inspired by autonomous agent frameworks like 
ReAct (Reason + Act).

At every step, the agent performs this loop until the LLM decides the task is "FINISH"ed.

1. **Perceive**: The agent "looks" at the current page. It doesn't read the raw, complex HTML. Instead, it runs the 
get_simplified_dom_string() function to build a simple, text-based representation of all interactive elements 
(buttons, links, inputs). This abstract view is perfect for an LLM.

Example "Simplified DOM":
```angular2html
<element id='1' type='input'>What needs to be done?</element>

```
2. **Capture**: Before acting, the agent captures a full-page screenshot of the current UI state and saves it to a 
task-specific folder (ex, `screenshots/create_a_new_project_in_linear.../`).
3. **Decide (The "Brain")**: The agent sends the Task, Action History, and Current Simplified DOM to an LLM (like GPT-4o). 
The LLM's sole job is to respond with a single JSON command, like:
   `{"action": "TYPE", "element_id": 1, "text": "New Project"}`
4. **Act (The "Hands")**: The script parses the JSON command and executes it. It uses `get_element_by_agent_id()` to find 
the Nth element on the page (ex, element_id: 1 is the 1st element). This "re-finding" logic is crucial for 
handling dynamic UIs and DOM re-renders. The loop repeats until the task is complete.

# How it Solves "Non-URL" States

This agent solves the "non-URL state" problem (like modals or forms that don't change the URL) by ignoring URLs entirely.

The agent's "state" is its perception of the current UI, which it re-evaluates every loop. When a modal appears, it 
simply sees a new list of interactive elements (like "Save", "Cancel") and acts accordingly.

For the interpretation task, you can choose from any of the six model providers: ChatGPT, Grok, Gemini, Claude, 
Perplexity, or DeepSeek. Just add your API keys to the `.env` file using the corresponding `<PROVIDER_API_KEY>`
variable names, and you’ll be all set.
