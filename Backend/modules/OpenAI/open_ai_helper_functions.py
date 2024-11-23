from modules.Utils.schema_class import RoleNotValid

def create_openai_obj(role: str, content: str) -> dict:
    if role not in {"user", "system", "assistant"}:
        raise RoleNotValid(role)
    return {
        "role": role,
        "content": content
    }