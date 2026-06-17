# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
it loads the listings from listings.json using the load_listings() function and using the query, filters them so we have a ranked list that match.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): a searching string that uses title, description, and style_tags
- `size` (str): a size filter, uses loose matching
- `max_price` (float): the maximum USD price. Don't include prices above this

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
returns a list of listing dicts sorted by their relevance. It is maxed to 5 returned.
**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
the tool will just return []. Won't call suggest outfit. It will suggest a broadening of the search criteria, giving specific relevant examples.

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
from the new listing list and wardrobe, it creates an outfit using the new item with the given wardrobe.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): a single listing dict from search_listings. it will have the title, colors, style_tags, and category tags.
- `wardrobe` (dict): a new wardrobe object that parallels the wardrobe_schema.json. It holds an items list. each item will have id, name, category, colors, style_tags, and notes.

**What it returns:**
<!-- Describe the return value -->
A dict that contains a pair of a suggestion and an items_used id value for the suggestion.
The suggestion will contain a short description of wardrobe pieces and how to style them specifically.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
is wardrobe.items is empty, don't use the tool at all. Instead, recommend the piece and suggest the user to add wardrobe items.

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Generates a small caption for the outfit to briefly describe it. Should feel casual.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (dict): the full dict from suggest_outfit

**What it returns:**
<!-- Describe the return value -->
returns a single string caption. Must be first person and casual. Must reference the item, the price, platform, and styling details.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
The tool card doesn't really need a fail condition because something can always be generated, it does not rely on any specific piece of information.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

parse the user's message and extract the query, size, max_price, and category. Then call the search_listings passing description, size, and max_price as parameters and store as session(results). If results is empty, set the session error to no results. Don't go to step 3.
step 3: call get_empty_wardrobe() or get_example_wardrobe(). store as session wardrobe. if wardrobe items is empty, surface the listing only, skip suggest_outfit and create_fit_card.
step 4: call suggest_wardrobe. pass both sessions selected_item and wardrobe. store as session outfit.
step 5: call create_fit_card and pass session outfit. store as session fit_card.
step 6: return the listing details, suggestion text, and fit card caption to user.
---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->



---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->
     ![architecture](IMG_0089.jpg)


---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

I will use Claude. I will feed it the tool 1 block containing inputs, return descriptions, and the failure condition, and load_listings(). I will ask it to verify the parameters are applied and the empty case returns an empty string. I will test with three queries, one with multiple matches, one with none, and one without sizes.

**Milestone 4 — Planning loop and state management:**
Using Claude again, I will feed it the Planning Loop section and the Architecture diagram from this file. I will ask it to implement the loop function that calls each tool in order and stores session state. I will verify by checking through the diagram. The early exit will fire and stop when search_listings returns [], and the wardrobe empty branch skips suggest_outfit and create_fit_card. Finally, session state keys (results, selected_item, wardrobe, outfit, fit_card) are set at each step



---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->

The agent calls search_listings("vintage graphic tee", size="M", max_price=30.0). It filters listings by category (tops), style tags (graphic tee, vintage), size, and price. The top result returned is: "Graphic Tee — 2003 Tour Bootleg Style, $24, Depop, good condition, black, size L."


**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->

With the top listing in hand, the agent calls suggest_outfit(new_item=bootleg tee, wardrobe=user's wardrobe). The wardrobe includes baggy straight-leg jeans (w_001), chunky white sneakers (w_007), and a vintage black denim jacket (w_006). The tool returns: "Wear the tee tucked loosely into your dark wash jeans with the chunky white sneakers. Layer the black denim jacket over the top, left open. Roll the sleeves once for shape."


**Step 3:**
<!-- Continue until the full interaction is complete -->

The agent calls create_fit_card(outfit=suggestion>, new_item=bootleg tee>). It generates a short, shareable caption styled like a thrift post: "thrifted this faded bootleg tee off depop for $24 and it was made for my baggy jeans 🖤 full look in my stories"


**Final output to user:**
<!-- What does the user actually see at the end? -->

The user sees the listing details (title, price, platform, condition), the outfit suggestion with specific pieces from their wardrobe, and the fit card caption ready to copy. If search_listings had returned no results, the agent would instead tell the user what to adjust — broader size range, higher price, or different keywords — and stop without calling the remaining tools.
