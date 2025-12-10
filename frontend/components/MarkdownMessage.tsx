"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark, oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";
import { FiCopy } from "react-icons/fi";

type Props = {
  content: string;
  theme?: "light" | "dark";
};

export default function MarkdownMessage({ content, theme = "dark" }: Props) {
  const isLight = theme === "light";

  return (
    <div
      className={`
        px-6 py-5 rounded-xl shadow-lg border
        max-w-4xl w-full
        ${
          isLight
            ? "bg-white border-gray-200 text-gray-900"
            : "bg-[#111827] border-gray-800 text-gray-100"
        }
      `}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1
              className={`text-2xl font-bold mt-6 mb-3 ${
                isLight ? "text-black" : "text-white"
              }`}
            >
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2
              className={`text-xl font-semibold mt-5 mb-3 ${
                isLight ? "text-black" : "text-white"
              }`}
            >
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3
              className={`text-lg font-semibold mt-4 mb-2 ${
                isLight ? "text-black" : "text-white"
              }`}
            >
              {children}
            </h3>
          ),

          p: ({ children }) => (
            <p className="leading-relaxed mb-3">{children}</p>
          ),

          ul: ({ children }) => (
            <ul className="list-disc ml-6 mb-3 space-y-1">{children}</ul>
          ),

          table: ({ children }) => (
            <table
              className={`w-full border-collapse rounded-lg overflow-hidden shadow-sm mb-4 ${
                isLight ? "border-gray-300" : "border-gray-700"
              }`}
            >
              {children}
            </table>
          ),

          th: ({ children }) => (
            <th
              className={`px-3 py-2 font-semibold text-left ${
                isLight ? "bg-gray-100 text-black" : "bg-gray-900 text-white"
              }`}
            >
              {children}
            </th>
          ),

          td: ({ children }) => (
            <td
              className={`px-3 py-2 border ${
                isLight ? "border-gray-300" : "border-gray-700"
              }`}
            >
              {children}
            </td>
          ),

          code({ inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");

            // Inline code 💡
            if (inline) {
              return (
                <code
                  className="px-1.5 py-1 rounded bg-gray-200 dark:bg-gray-800 text-pink-600 dark:text-pink-400"
                  {...props}
                >
                  {children}
                </code>
              );
            }

            // Code block 💡
            return (
              <div className="relative group mt-4 mb-6">
                {/* Copy Button */}
                <button
                  onClick={() => navigator.clipboard.writeText(String(children))}
                  className={`
                    absolute right-2 top-2 p-2 rounded-md 
                    transition-all opacity-60 group-hover:opacity-100
                    ${
                      isLight
                        ? "bg-white text-black border border-gray-300"
                        : "bg-gray-900 text-white border border-gray-700"
                    }
                  `}
                >
                  <FiCopy size={16} />
                </button>

                <SyntaxHighlighter
                  PreTag="div"
                  language={match?.[1] || "text"}
                  style={isLight ? oneLight : oneDark}
                  customStyle={{
                    padding: "18px",
                    borderRadius: "12px",
                    fontSize: "14px",
                  }}
                  {...props}
                >
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              </div>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}