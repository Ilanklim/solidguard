import type * as Monaco from "monaco-editor";

export const solidityLanguageDefinition: Monaco.languages.IMonarchLanguage = {
  defaultToken: "",
  tokenPostfix: ".sol",

  keywords: [
    "pragma",
    "solidity",
    "import",
    "as",
    "from",
    "contract",
    "interface",
    "library",
    "is",
    "struct",
    "enum",
    "event",
    "using",
    "assembly",
    "function",
    "modifier",
    "constructor",
    "fallback",
    "receive",
    "error",
    "public",
    "private",
    "internal",
    "external",
    "pure",
    "view",
    "payable",
    "constant",
    "immutable",
    "override",
    "virtual",
    "returns",
    "memory",
    "storage",
    "calldata",
    "if",
    "else",
    "for",
    "while",
    "do",
    "break",
    "continue",
    "return",
    "throw",
    "emit",
    "try",
    "catch",
    "revert",
    "require",
    "assert",
    "new",
    "delete",
    "mapping",
    "indexed",
    "anonymous",
    "unchecked",
    "abstract",
    "type",
  ],

  typeKeywords: [
    "address",
    "bool",
    "string",
    "bytes",
    "byte",
    "int",
    "int8",
    "int16",
    "int24",
    "int32",
    "int40",
    "int48",
    "int56",
    "int64",
    "int72",
    "int80",
    "int88",
    "int96",
    "int104",
    "int112",
    "int120",
    "int128",
    "int136",
    "int144",
    "int152",
    "int160",
    "int168",
    "int176",
    "int184",
    "int192",
    "int200",
    "int208",
    "int216",
    "int224",
    "int232",
    "int240",
    "int248",
    "int256",
    "uint",
    "uint8",
    "uint16",
    "uint24",
    "uint32",
    "uint40",
    "uint48",
    "uint56",
    "uint64",
    "uint72",
    "uint80",
    "uint88",
    "uint96",
    "uint104",
    "uint112",
    "uint120",
    "uint128",
    "uint136",
    "uint144",
    "uint152",
    "uint160",
    "uint168",
    "uint176",
    "uint184",
    "uint192",
    "uint200",
    "uint208",
    "uint216",
    "uint224",
    "uint232",
    "uint240",
    "uint248",
    "uint256",
    "bytes1",
    "bytes2",
    "bytes3",
    "bytes4",
    "bytes5",
    "bytes6",
    "bytes7",
    "bytes8",
    "bytes9",
    "bytes10",
    "bytes11",
    "bytes12",
    "bytes13",
    "bytes14",
    "bytes15",
    "bytes16",
    "bytes17",
    "bytes18",
    "bytes19",
    "bytes20",
    "bytes21",
    "bytes22",
    "bytes23",
    "bytes24",
    "bytes25",
    "bytes26",
    "bytes27",
    "bytes28",
    "bytes29",
    "bytes30",
    "bytes31",
    "bytes32",
    "fixed",
    "ufixed",
  ],

  constants: ["true", "false", "wei", "gwei", "ether", "seconds", "minutes", "hours", "days", "weeks", "years"],

  builtins: [
    "msg",
    "block",
    "tx",
    "abi",
    "this",
    "super",
    "selfdestruct",
    "suicide",
    "now",
    "gasleft",
    "blockhash",
    "keccak256",
    "sha256",
    "ripemd160",
    "ecrecover",
    "addmod",
    "mulmod",
  ],

  operators: [
    "=",
    ">",
    "<",
    "!",
    "~",
    "?",
    ":",
    "==",
    "<=",
    ">=",
    "!=",
    "&&",
    "||",
    "++",
    "--",
    "+",
    "-",
    "*",
    "/",
    "&",
    "|",
    "^",
    "%",
    "<<",
    ">>",
    ">>>",
    "+=",
    "-=",
    "*=",
    "/=",
    "&=",
    "|=",
    "^=",
    "%=",
    "<<=",
    ">>=",
    ">>>=",
    "**",
  ],

  symbols: /[=><!~?:&|+\-*\/\^%]+/,

  escapes: /\\(?:[abfnrtv\\"']|x[0-9A-Fa-f]{1,4}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})/,

  tokenizer: {
    root: [
      // SPDX license identifier
      [/\/\/\s*SPDX-License-Identifier:.*$/, "comment.doc"],

      // Comments
      [/\/\/.*$/, "comment"],
      [/\/\*/, "comment", "@comment"],

      // Natspec
      [/\/\/\/.*$/, "comment.doc"],
      [/\/\*\*/, "comment.doc", "@natspec"],

      // Strings
      [/"([^"\\]|\\.)*$/, "string.invalid"],
      [/'([^'\\]|\\.)*$/, "string.invalid"],
      [/"/, "string", "@string_double"],
      [/'/, "string", "@string_single"],

      // Hex literals
      [/hex"[0-9A-Fa-f]*"/, "number.hex"],
      [/hex'[0-9A-Fa-f]*'/, "number.hex"],

      // Numbers
      [/\d*\.\d+([eE][\-+]?\d+)?/, "number.float"],
      [/0[xX][0-9a-fA-F]+/, "number.hex"],
      [/\d+/, "number"],

      // Identifiers and keywords
      [
        /[a-zA-Z_$][\w$]*/,
        {
          cases: {
            "@keywords": "keyword",
            "@typeKeywords": "type",
            "@constants": "constant",
            "@builtins": "variable.predefined",
            "@default": "identifier",
          },
        },
      ],

      // Whitespace
      { include: "@whitespace" },

      // Delimiters and operators
      [/[{}()\[\]]/, "@brackets"],
      [/[<>](?!@symbols)/, "@brackets"],
      [
        /@symbols/,
        {
          cases: {
            "@operators": "operator",
            "@default": "",
          },
        },
      ],

      // Delimiter
      [/[;,.]/, "delimiter"],
    ],

    comment: [
      [/[^\/*]+/, "comment"],
      [/\*\//, "comment", "@pop"],
      [/[\/*]/, "comment"],
    ],

    natspec: [
      [/[^\/*]+/, "comment.doc"],
      [/\*\//, "comment.doc", "@pop"],
      [/[\/*]/, "comment.doc"],
    ],

    string_double: [
      [/[^\\"]+/, "string"],
      [/@escapes/, "string.escape"],
      [/\\./, "string.escape.invalid"],
      [/"/, "string", "@pop"],
    ],

    string_single: [
      [/[^\\']+/, "string"],
      [/@escapes/, "string.escape"],
      [/\\./, "string.escape.invalid"],
      [/'/, "string", "@pop"],
    ],

    whitespace: [[/[ \t\r\n]+/, "white"]],
  },
};

export function registerSolidityLanguage(monaco: typeof Monaco) {
  // Check if already registered
  const languages = monaco.languages.getLanguages();
  if (languages.some((lang) => lang.id === "solidity")) {
    return;
  }

  monaco.languages.register({ id: "solidity" });
  monaco.languages.setMonarchTokensProvider("solidity", solidityLanguageDefinition);

  // Define a custom theme for Solidity that matches our dark UI
  monaco.editor.defineTheme("solidguard-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "22d3ee", fontStyle: "bold" }, // cyan
      { token: "type", foreground: "a78bfa" }, // purple
      { token: "constant", foreground: "f472b6" }, // pink
      { token: "variable.predefined", foreground: "fbbf24" }, // amber
      { token: "string", foreground: "86efac" }, // green
      { token: "string.escape", foreground: "6ee7b7" },
      { token: "number", foreground: "f97316" }, // orange
      { token: "number.hex", foreground: "fb923c" },
      { token: "number.float", foreground: "f97316" },
      { token: "comment", foreground: "64748b", fontStyle: "italic" }, // slate
      { token: "comment.doc", foreground: "94a3b8", fontStyle: "italic" },
      { token: "operator", foreground: "22d3ee" },
      { token: "delimiter", foreground: "94a3b8" },
      { token: "identifier", foreground: "e2e8f0" },
    ],
    colors: {
      "editor.background": "#0a0f1a",
      "editor.foreground": "#e2e8f0",
      "editor.lineHighlightBackground": "#1e293b40",
      "editorLineNumber.foreground": "#475569",
      "editorLineNumber.activeForeground": "#22d3ee",
      "editor.selectionBackground": "#22d3ee30",
      "editor.inactiveSelectionBackground": "#22d3ee20",
      "editorCursor.foreground": "#22d3ee",
      "editorGutter.background": "#0a0f1a",
    },
  });
}
