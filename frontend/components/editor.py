from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class EditorState:
    code: str


LANGUAGE_SNIPPETS: dict[str, str] = {
    "Python": 'def hello(name: str) -> str:\n    return f"Hello, {name}!"\n',
    "JavaScript": 'function hello(name) {\n  return `Hello, ${name}!`;\n}\n',
    "TypeScript": 'function hello(name: string): string {\n  return `Hello, ${name}!`;\n}\n',
    "Go": 'package main\n\nfunc hello(name string) string {\n\treturn "Hello, " + name + "!"\n}\n',
    "Java": 'public class Hello {\n    public static String hello(String name) {\n        return "Hello, " + name + "!";\n    }\n}\n',
    "Rust": 'fn hello(name: &str) -> String {\n    format!("Hello, {}!", name)\n}\n',
    "YAML": 'service:\n  name: hello\n  enabled: true\n',
    "Markdown": '# Review notes\n\n- Capture findings here\n- Add follow-up items\n',
}


def render_code_editor(language: str) -> EditorState:
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown("### Code editor")
    st.caption("Local editing surface for review input. The backend is not connected yet.")

    default_code = LANGUAGE_SNIPPETS.get(language, LANGUAGE_SNIPPETS["Python"])
    code = st.text_area(
        "Code input",
        value=st.session_state.get("code_editor_value", default_code),
        height=360,
        key="code_editor_value",
        help="Paste the code or diff you want to inspect.",
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)
    return EditorState(code=code.strip())
