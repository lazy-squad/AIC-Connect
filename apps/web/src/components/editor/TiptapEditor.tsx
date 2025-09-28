'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import Placeholder from '@tiptap/extension-placeholder';
import { common, createLowlight } from 'lowlight';
import EditorToolbar from './EditorToolbar';

const lowlight = createLowlight(common);

interface TiptapEditorProps {
  content?: any;
  onChange: (content: any) => void;
  placeholder?: string;
  editable?: boolean;
  className?: string;
}

export default function TiptapEditor({
  content,
  onChange,
  placeholder = 'Start writing...',
  editable = true,
  className = '',
}: TiptapEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        bulletList: {
          keepMarks: true,
          keepAttributes: false,
        },
        orderedList: {
          keepMarks: true,
          keepAttributes: false,
        },
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-600 hover:text-blue-800 underline',
        },
      }),
      CodeBlockLowlight.configure({
        lowlight,
      }),
      Placeholder.configure({
        placeholder,
      }),
    ],
    content,
    editable,
    onUpdate: ({ editor }) => {
      onChange(editor.getJSON());
    },
  });

  return (
    <div className={`border border-gray-300 rounded-lg overflow-hidden ${className}`}>
      {editable && editor && (
        <EditorToolbar editor={editor} variant="full" />
      )}
      <EditorContent
        editor={editor}
        className="prose prose-sm max-w-none p-4 min-h-[200px] focus:outline-none"
      />
    </div>
  );
}