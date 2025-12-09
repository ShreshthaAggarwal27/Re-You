"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";

export default function MarkdownMessage({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || "");

          return !inline ? (
            <SyntaxHighlighter language={match?.[1] || "javascript"}>
              {String(children).replace(/\n$/, "")}
            </SyntaxHighlighter>
          ) : (
            <code className="bg-slate-800/60 px-1 py-0.5 rounded" {...props}>
              {children}
            </code>
          );
        }
      }}
    >
      {content}
    </ReactMarkdown>
  );
}