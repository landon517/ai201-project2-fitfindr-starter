# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.


## Tool Inventory
 
### `search_listings(description, size, max_price)`
 
**Purpose:** Searches the mock listings dataset for items matching the user's query. This is a pure filtering and ranking function — no LLM involved.
 
**Inputs:**
- `description` (`str`): Natural language keywords matched against each listing's title, description, and style tags.
- `size` (`str | None`): Size filter using loose case-insensitive substring matching (e.g., `"M"` matches `"S/M"` and `"M/L"`). Pass `None` to skip size filtering.
- `max_price` (`float | None`): Maximum price in USD, inclusive. Pass `None` to skip price filtering.
**Output:** A list of up to 5 listing dicts sorted by relevance score (number of description keywords matched). Returns `[]` if nothing matches — never raises an exception.
 
---
 
### `suggest_outfit(new_item, wardrobe)`
 
**Purpose:** Given the thrifted item and the user's wardrobe, calls the Groq LLM to suggest 1–2 complete outfits. Handles the empty wardrobe case gracefully by switching to a general styling prompt.
 
**Inputs:**
- `new_item` (`dict`): A listing dict from `search_listings`. Uses `title`, `colors`, `style_tags`, and `category`.
- `wardrobe` (`dict`): A wardrobe object with an `items` list. Each item has `id`, `name`, `category`, `colors`, `style_tags`, and optional `notes`.
**Output:** A non-empty string with outfit suggestions. If the wardrobe is empty, returns general styling advice instead of crashing.
 
---
 
### `create_fit_card(outfit, new_item)`
 
**Purpose:** Generates a short, casual social-media-style caption for the outfit. Uses a higher LLM temperature (1.1) so the output varies across runs.
 
**Inputs:**
- `outfit` (`str`): The suggestion string from `suggest_outfit`.
- `new_item` (`dict`): The listing dict. Uses `title`, `price`, and `platform`.
**Output:** A 2–4 sentence first-person caption mentioning the item, price, and platform. If `outfit` is empty or whitespace-only, returns a descriptive error string rather than raising an exception.
 
---
 
## How the Planning Loop Works
 
The agent does not call all three tools unconditionally. It runs a linear loop with two early-exit conditions:
 
1. **Parse the query** using regex to extract a keyword description, optional size, and optional price ceiling.
2. **Call `search_listings`** with the parsed parameters. If the result is an empty list, the agent immediately sets `session["error"]` to a message telling the user what failed and what to try differently, then returns early — `suggest_outfit` and `create_fit_card` are never called.
3. **Select the top result** (`results[0]`) and store it as `session["selected_item"]`.
4. **Check the wardrobe.** If `wardrobe["items"]` is empty, `suggest_outfit` is still called — but with a prompt that asks for general styling advice rather than specific pairings.
5. **Call `suggest_outfit`** with the selected item and the wardrobe. Store the result in `session["outfit_suggestion"]`.
6. **Call `create_fit_card`** with the outfit string and selected item. Store in `session["fit_card"]`.
7. **Return the session dict.** The caller checks `session["error"]` first; if it is `None`, all three output fields are populated.
The key design decision is that `suggest_outfit` is never called with empty input from `search_listings`. The branch on step 2 is what makes the agent's behavior differ based on input rather than always running the same sequence.
 
---
 
## State Management
 
All state for a single interaction lives in one session dict initialized by `_new_session()`:
 
```python
{
    "query": str,               # original user input
    "parsed": dict,             # extracted description, size, max_price
    "search_results": list,     # all matches from search_listings
    "selected_item": dict,      # results[0], passed into suggest_outfit
    "wardrobe": dict,           # user's wardrobe
    "outfit_suggestion": str,   # returned by suggest_outfit
    "fit_card": str,            # returned by create_fit_card
    "error": str | None,        # set on early exit, None on success
}
```
 
Each tool's output is stored in the session before the next tool is called, so every step reads from the same dict. There is no re-prompting or re-fetching — `session["selected_item"]` that goes into `suggest_outfit` is the exact same dict that came out of `search_listings`.
 
---
 
## Error Handling
 
| Tool | Failure mode | Agent response |
|---|---|---|
| `search_listings` | No listings match the query | Sets `session["error"]`: "No listings matched '[query]' in size [X] under $[Y]. Try broadening your size range, raising your budget, or using different keywords like 'band tee', 'graphic shirt', or 'flannel'." Returns early — does not call the other tools. |
| `suggest_outfit` | Wardrobe is empty | Still calls the LLM with a general styling prompt. Returns non-empty styling advice rather than crashing or returning an empty string. |
| `create_fit_card` | `outfit` is empty or whitespace | Returns the string: "Error: outfit suggestion is missing — run suggest_outfit first before generating a fit card." Does not raise an exception. |
 
**Concrete example from testing:**
 
Running the no-results path:
```
python agent.py
```
Output for the "designer ballgown size XXS under $5" test case:
```
Error message: No listings matched "designer ballgown" in size XXS under $5.
Try broadening your size range, raising your budget, or using different
keywords like 'band tee', 'graphic shirt', or 'flannel'.
fit_card is None: True
```
`suggest_outfit` and `create_fit_card` were never called.
 
---
 
## Spec Reflection
 
The planning.md spec held up well through implementation with two adjustments:
 
**Query parsing:** The spec said to parse description, size, and max_price from the user's message but didn't specify how. I implemented this with regex rather than an LLM call — it's faster, cheaper, and deterministic, which matters for a step that runs on every query. The tradeoff is that unusual phrasings (e.g., "no more than thirty dollars") won't be caught, but for the scope of this project the regex covers all realistic inputs.
 
**`create_fit_card` signature:** The spec listed only `outfit` as a parameter, but the stub in `tools.py` also included `new_item`. Keeping `new_item` made the captions significantly more specific (item name, price, platform appear naturally), so the stub signature was the right call over the spec.
 
---
 
## AI Tool Usage
 
**Instance 1 — implementing `search_listings`:**
I gave Claude the Tool 1 block from `planning.md` (the inputs table, return value description, and empty-result failure mode) along with the `load_listings()` function signature from `data_loader.py`. I asked it to implement the function using those helpers. The generated code used `in` substring matching for size and scored by keyword count across title, description, and style tags — matching the spec. I verified that (1) all three filter parameters were applied, (2) the empty-result case returned `[]` not `None`, and (3) results were sorted by score. I added the cap of 5 results, which the generated code omitted.
 
**Instance 2 — implementing the planning loop:**
I gave Claude the Planning Loop section and the Mermaid architecture diagram from `planning.md` and asked it to implement `run_agent()`. The generated code correctly branched on empty search results and stored values in the session dict at each step. I changed one thing: the generated code called `suggest_outfit` with a hardcoded empty wardrobe check inside `run_agent()` and passed a modified wardrobe in — I moved that logic back into `suggest_outfit` itself, where the spec said it belonged, so the tool handles its own failure mode rather than the planning loop working around it.

