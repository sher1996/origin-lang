import React, { useEffect, useRef, useState } from 'react';

interface PreviewPaneProps {
  code: string;
  isError: boolean;
  errorMessage?: string;
}

const PreviewPane: React.FC<PreviewPaneProps> = ({ code, isError, errorMessage }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [output, setOutput] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!iframeRef.current) return;

    setIsLoading(true);
    
    // Create the HTML content for the iframe
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Origin Preview</title>
  <style>
    body {
      font-family: 'Courier New', monospace;
      margin: 0;
      padding: 16px;
      background: #1e1e1e;
      color: #d4d4d4;
      font-size: 14px;
      line-height: 1.4;
    }
    .output {
      white-space: pre-wrap;
      word-wrap: break-word;
    }
    .error {
      color: #f44336;
      background: rgba(244, 67, 54, 0.1);
      padding: 8px;
      border-radius: 4px;
      margin: 8px 0;
    }
    .loading {
      color: #888;
      font-style: italic;
    }
  </style>
</head>
<body>
  <div id="output" class="output">
    <div class="loading">Loading...</div>
  </div>
  
  <script>
    // Capture console.log for preview
    const originalLog = console.log;
    const outputDiv = document.getElementById('output');
    
    console.log = function(...args) {
      const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
      ).join(' ');
      outputDiv.innerHTML += message + '\\n';
      originalLog.apply(console, args);
    };
    
    // Simple Origin-like interpreter for preview
    function interpretOrigin(code) {
      const lines = code.split('\\n').filter(line => line.trim());
      let variables = {};
      
      for (const line of lines) {
        const trimmed = line.trim();
        
        if (trimmed.startsWith('say ')) {
          const expr = trimmed.substring(4);
          try {
            // Simple expression evaluation
            const result = eval(expr.replace(/\\b(\\w+)\\b/g, (match, varName) => {
              return variables[varName] !== undefined ? variables[varName] : match;
            }));
            console.log(result);
          } catch (error) {
            console.log('Error:', error.message);
          }
        } else if (trimmed.startsWith('let ')) {
          const match = trimmed.match(/let (\\w+) = (.+)/);
          if (match) {
            const [, name, expr] = match;
            try {
              const value = eval(expr.replace(/\\b(\\w+)\\b/g, (match, varName) => {
                return variables[varName] !== undefined ? variables[varName] : match;
              }));
              variables[name] = value;
            } catch (error) {
              console.log('Error:', error.message);
            }
          }
        } else if (trimmed.startsWith('repeat ')) {
          const match = trimmed.match(/repeat (\\d+) times:/);
          if (match) {
            const count = parseInt(match[1]);
            // For now, just log the repeat instruction
            console.log(\`Repeat \${count} times\`);
          }
        }
      }
    }
    
    // Listen for messages from parent
    window.addEventListener('message', function(event) {
      if (event.data.type === 'execute') {
        outputDiv.innerHTML = '';
        try {
          interpretOrigin(event.data.code);
        } catch (error) {
          outputDiv.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
        }
      }
    });
    
    // Notify parent that we're ready
    window.parent.postMessage({ type: 'ready' }, '*');
  </script>
</body>
</html>`;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    
    iframeRef.current.src = url;
    
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'ready') {
        setIsLoading(false);
        // Execute the code
        iframeRef.current?.contentWindow?.postMessage({
          type: 'execute',
          code: code
        }, '*');
      } else if (event.data.type === 'output') {
        setOutput(event.data.output);
      }
    };
    
    window.addEventListener('message', handleMessage);
    
    return () => {
      window.removeEventListener('message', handleMessage);
      URL.revokeObjectURL(url);
    };
  }, [code]);

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      <div className="bg-gray-800 px-4 py-2 border-b border-gray-700">
        <h3 className="text-sm font-medium">Live Preview</h3>
      </div>
      
      <div className="flex-1 relative">
        {isError && errorMessage && (
          <div className="absolute inset-0 bg-red-900 bg-opacity-90 flex items-center justify-center z-10">
            <div className="bg-red-800 p-4 rounded-lg max-w-md">
              <h4 className="text-red-200 font-medium mb-2">Error</h4>
              <p className="text-red-100 text-sm">{errorMessage}</p>
            </div>
          </div>
        )}
        
        {isLoading && (
          <div className="absolute inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center z-5">
            <div className="text-gray-400">Loading preview...</div>
          </div>
        )}
        
        <iframe
          ref={iframeRef}
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-same-origin"
          title="Origin Preview"
        />
      </div>
    </div>
  );
};

export default PreviewPane; 