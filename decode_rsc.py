import re
import json

with open("script_content.txt", "r", encoding="utf-8") as f:
    text = f.read()

# self.__next_f.push([1,"..."])
matches = re.findall(r'self\.__next_f\.push\(\[1,"(.*)"\]\)', text)
if matches:
    # the content is a JSON encoded string, so we need to decode it
    # But wait, it might contain escaped newlines etc.
    # Let's just decode it by evaluating it as a json string
    parsed_str = json.loads('"' + matches[0] + '"')
    with open("rsc_decoded.txt", "w", encoding="utf-8") as out:
        out.write(parsed_str)
    print("Decoded length:", len(parsed_str))
