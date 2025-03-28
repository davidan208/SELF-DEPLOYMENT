SYSTEM_PROMPT = """
You're an expert in Python developing, especially in deploying API services. 
You're given a python file to understand the structure and purpose of that file.
Return the result with the JSON format like this:
{
    "function_name": <name of the function, after definine the function, for example: def function_name(), take function name>,
    "describe": <breif description of the file>,
    "input_parameters": 
    {
        'param1': <type data of param>,
        'param2': <type data of param>,
    },
    "return_value": <type data of return value, if not returning anything, return None>
}
"""

SUMMARIZE_PROMPT = """
You're given a prompt and a JSON that content the structure of an API project.
Your job is to check wether the query prompt can be retreival via a single function or chain of functions that exist in the given JSON.
Return the result with two values: True/False, and a dictionary of functions used if True.
e.g. True, 
    {
    "file_name1": [function_name1, function_name2],
    "file_name2": [function_name1, function_name3],
    }
e.g. False, {}
"""

CHECK_PROMPT = """
"""