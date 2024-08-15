# Extract Meanings, Translate, and Create Examples

Extract meanings, provide translations, and create examples from the provided text, considering the context and different forms of words. Limit examples and entries as specified.

## CSV File Format

Create a CSV file with the following columns in this exact order:
1. **English Phrase**: The word or phrase exactly as it appears in the text
2. **Vietnamese Translation / Part of Speech and Meaning**: Provide the translation of the phrase, followed by a forward slash (/), then the part of speech in parentheses and a brief meaning
3. **Example**: The full sentence or phrase containing the word, with the target phrase in bold

## CSV Generation Guidelines

- Do not include a header row
- Start data from the first line
- Ensure strict adherence to the specified format
- Process words and their forms from the input text, with limitations
- Produce only the CSV content, without additional explanations
- Double-check each entry for accuracy, especially the translations and examples

## Example 
Example of input:
```
salute noun

1 military gesture

ADJ.
military, naval | smart | mock
VERB + SALUTE
give (sb)
The sentry gave a smart salute and waved us on.
| acknowledge, return | take
The Queen took the salute as the guardsmen marched past.

2 action of respect or welcome

ADJ.
final, last | 21-gun, etc. | special | triumphant, victory
PREP.
in ~
The guests raised their glasses in salute.
| ~ from
The retiring editor received a special salute from the local newspaper.
| ~ to
His first words were a salute to the people of South Africa.

salute verb

ADV.
smartly
The captain stood to attention and saluted smartly.

PREP.
with
He saluted Pippa with a graceful bend of his head.
```

Here's the example of correct output CSV: 
```code
give a smart salute,chào nghiêm chỉnh / (noun) A military gesture,The sentry **give a smart salute** and waved us on.
in salute,nâng ly chúc mừng / (noun) An action of respect or welcome,The guests raise glasses **in salute**.
saluted smartly,chào một cách khôn ngoan / (verb) A formal gesture of respect or recognition,The captain stood to attention and **saluted smartly**.
```

## Additional Instructions

- For each available form (noun, verb, PREP, adv, etc.) and each distinct meaning, provide only ONE example
- Include a maximum of 5 entries in total, regardless of the number of forms or meanings
- If there are more than 5 possible entries, prioritize the most common or significant uses
- Ensure all translations, meanings, and examples are accurate and appropriate for the context
- Verify that the bolded phrases in the examples are correct and match the English phrase exactly as it appears in the text

## Output Requirements

- Adhere strictly to the limit of one example per form/meaning and maximum 5 entries total
- Double-check format compliance for each entry
- Ensure translations and meanings accurately reflect the contextual usage
- Provide only the CSV content for easy copying and use
- Use artifact code to present the CSV content
- After generating the CSV, review each entry to confirm the accuracy of translations, meanings, and examples

## Quality Control

- After completing the CSV, review all entries to ensure adherence to the new limitations
- Verify that each form and meaning has only one example, and that there are no more than 5 entries total
- Confirm that each English phrase in the first column is exactly as it appears in the original text, without any modifications or simplifications
- If any errors are found during this check, review and correct all entries before finalizing the CSV
- If asked to update or correct an entry, carefully review the entire CSV again to ensure no other similar errors exist and that the entry limits are still respected

When you have processed the text and created the CSV file, please provide the entire CSV content within an artifact, similar to the example entries provided above. Always be prepared to make corrections if errors are pointed out.

## Input Format

The input will be provided in the following format:

Given the context below:
- Extract the meaning and one example of each form
- Provide a Vietnamese translation for each phrase
- Limit to one example per form/meaning and maximum 5 entries total

[Input text with words and their forms, meanings, and examples]

## Output Format

The output should be the CSV content as described above, presented within an artifact, with strict adherence to the entry limitations and exact phrase matching.