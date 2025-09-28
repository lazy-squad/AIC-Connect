'use client';

import { Editor } from '@tiptap/react';

interface EditorToolbarProps {
  editor: Editor;
  variant?: 'full' | 'minimal';
}

export default function EditorToolbar({ editor, variant = 'full' }: EditorToolbarProps) {
  const Button = ({
    onClick,
    isActive = false,
    disabled = false,
    children,
    title,
  }: {
    onClick: () => void;
    isActive?: boolean;
    disabled?: boolean;
    children: React.ReactNode;
    title?: string;
  }) => (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`
        px-3 py-1.5 text-sm font-medium rounded transition-colors
        ${isActive
          ? 'bg-gray-200 text-gray-900'
          : 'text-gray-700 hover:bg-gray-100'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      {children}
    </button>
  );

  return (
    <div className="border-b border-gray-300 bg-gray-50 p-2 flex flex-wrap gap-1">
      <div className="flex gap-1">
        <Button
          onClick={() => editor.chain().focus().toggleBold().run()}
          isActive={editor.isActive('bold')}
          title="Bold (Ctrl+B)"
        >
          B
        </Button>
        <Button
          onClick={() => editor.chain().focus().toggleItalic().run()}
          isActive={editor.isActive('italic')}
          title="Italic (Ctrl+I)"
        >
          <i>I</i>
        </Button>
        <Button
          onClick={() => editor.chain().focus().toggleStrike().run()}
          isActive={editor.isActive('strike')}
          title="Strikethrough"
        >
          <s>S</s>
        </Button>
        <Button
          onClick={() => editor.chain().focus().toggleCode().run()}
          isActive={editor.isActive('code')}
          title="Code"
        >
          {'</>'}
        </Button>
      </div>

      {variant === 'full' && (
        <>
          <div className="w-px h-6 bg-gray-300 mx-1" />

          <div className="flex gap-1">
            <Button
              onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
              isActive={editor.isActive('heading', { level: 2 })}
              title="Heading 2"
            >
              H2
            </Button>
            <Button
              onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
              isActive={editor.isActive('heading', { level: 3 })}
              title="Heading 3"
            >
              H3
            </Button>
          </div>

          <div className="w-px h-6 bg-gray-300 mx-1" />

          <div className="flex gap-1">
            <Button
              onClick={() => editor.chain().focus().toggleBulletList().run()}
              isActive={editor.isActive('bulletList')}
              title="Bullet List"
            >
              • List
            </Button>
            <Button
              onClick={() => editor.chain().focus().toggleOrderedList().run()}
              isActive={editor.isActive('orderedList')}
              title="Ordered List"
            >
              1. List
            </Button>
            <Button
              onClick={() => editor.chain().focus().toggleBlockquote().run()}
              isActive={editor.isActive('blockquote')}
              title="Blockquote"
            >
              "
            </Button>
            <Button
              onClick={() => editor.chain().focus().toggleCodeBlock().run()}
              isActive={editor.isActive('codeBlock')}
              title="Code Block"
            >
              {'<>'}
            </Button>
          </div>

          <div className="w-px h-6 bg-gray-300 mx-1" />

          <div className="flex gap-1">
            <Button
              onClick={() => {
                const url = window.prompt('Enter URL');
                if (url) {
                  editor.chain().focus().setLink({ href: url }).run();
                }
              }}
              isActive={editor.isActive('link')}
              title="Add Link"
            >
              Link
            </Button>
            {editor.isActive('link') && (
              <Button
                onClick={() => editor.chain().focus().unsetLink().run()}
                title="Remove Link"
              >
                Unlink
              </Button>
            )}
          </div>
        </>
      )}

      <div className="w-px h-6 bg-gray-300 mx-1" />

      <div className="flex gap-1">
        <Button
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          title="Undo (Ctrl+Z)"
        >
          ↶
        </Button>
        <Button
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          title="Redo (Ctrl+Y)"
        >
          ↷
        </Button>
      </div>
    </div>
  );
}