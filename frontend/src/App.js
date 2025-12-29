import React, { useState, useCallback } from 'react';
import { FileUp, Code, Download, Trash2, FileText, Loader2 } from 'lucide-react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Textarea } from './components/ui/textarea';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

const SAMPLE_SOP = `1. Receive customer support email.
2. Check if the issue is billing-related.
3. If yes, assign to Billing Queue.
4. If no, assign to General Support Queue.
5. Send acknowledgment email to customer.
6. Close the triage step.`;

function App() {
  const [sopText, setSopText] = useState('');
  const [processName, setProcessName] = useState('SOP Process');
  const [bpmnXml, setBpmnXml] = useState('');
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleTextConversion = async () => {
    if (!sopText.trim()) return;

    setIsLoading(true);
    setBpmnXml('');
    setStats(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/convert/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: sopText, process_name: processName })
      });

      const data = await response.json();

      if (data.success) {
        setBpmnXml(data.bpmn_xml);
        setStats(data.stats);
      }
    } catch (err) {
      console.error('Conversion failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileConversion = async () => {
    if (!uploadedFile) return;

    setIsLoading(true);
    setBpmnXml('');
    setStats(null);

    const formData = new FormData();
    formData.append('file', uploadedFile);
    formData.append('process_name', processName);

    try {
      const response = await fetch(`${BACKEND_URL}/api/convert/file`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        setBpmnXml(data.bpmn_xml);
        setStats(data.stats);
      }
    } catch (err) {
      console.error('Conversion failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileDrop = useCallback((e) => {
    e.preventDefault();
    const file = e.dataTransfer?.files?.[0] || e.target?.files?.[0];
    if (file) {
      const validTypes = ['.docx', '.txt', '.doc'];
      const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
      if (validTypes.includes(ext)) {
        setUploadedFile(file);
      }
    }
  }, []);

  const downloadBpmn = () => {
    if (!bpmnXml) return;
    const blob = new Blob([bpmnXml], { type: 'application/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${processName.replace(/\s+/g, '_')}.bpmn`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const loadSample = () => {
    setSopText(SAMPLE_SOP);
  };

  const clearAll = () => {
    setSopText('');
    setBpmnXml('');
    setStats(null);
    setUploadedFile(null);
    setProcessName('SOP Process');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
              <Code className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-foreground">SOP to BPMN Converter</h1>
              <p className="text-sm text-muted-foreground">Transform SOPs into BPMN 2.0 diagrams</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Input Section */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Input SOP</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <Label htmlFor="processName" className="text-sm font-medium">Process Name</Label>
                <Input
                  id="processName"
                  value={processName}
                  onChange={(e) => setProcessName(e.target.value)}
                  placeholder="Enter process name"
                  className="mt-1.5"
                />
              </div>

              <Tabs defaultValue="text" className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-4">
                  <TabsTrigger value="text" className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Text
                  </TabsTrigger>
                  <TabsTrigger value="file" className="flex items-center gap-2">
                    <FileUp className="w-4 h-4" />
                    File
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="text">
                  <div className="space-y-3">
                    <Textarea
                      value={sopText}
                      onChange={(e) => setSopText(e.target.value)}
                      placeholder="Enter SOP steps here..."
                      className="min-h-[280px] font-mono text-sm resize-none"
                    />
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={loadSample}>
                        Load Sample
                      </Button>
                      <Button
                        onClick={handleTextConversion}
                        disabled={isLoading || !sopText.trim()}
                        className="ml-auto"
                      >
                        {isLoading ? (
                          <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Converting...</>
                        ) : (
                          <><Code className="w-4 h-4 mr-2" />Convert</>
                        )}
                      </Button>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="file">
                  <div className="space-y-3">
                    <div
                      onDrop={handleFileDrop}
                      onDragOver={(e) => e.preventDefault()}
                      className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors cursor-pointer"
                      onClick={() => document.getElementById('fileInput').click()}
                    >
                      <input
                        id="fileInput"
                        type="file"
                        accept=".docx,.txt,.doc"
                        onChange={handleFileDrop}
                        className="hidden"
                      />
                      <FileUp className="w-10 h-10 mx-auto mb-3 text-muted-foreground" />
                      {uploadedFile ? (
                        <div className="space-y-1">
                          <p className="font-medium text-foreground">{uploadedFile.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {(uploadedFile.size / 1024).toFixed(1)} KB
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-1">
                          <p className="text-foreground">Drop file here or click to upload</p>
                          <p className="text-sm text-muted-foreground">Supports .docx and .txt</p>
                        </div>
                      )}
                    </div>

                    <div className="flex gap-2">
                      {uploadedFile && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setUploadedFile(null)}
                        >
                          <Trash2 className="w-4 h-4 mr-1" />
                          Remove
                        </Button>
                      )}
                      <Button
                        onClick={handleFileConversion}
                        disabled={isLoading || !uploadedFile}
                        className="ml-auto"
                      >
                        {isLoading ? (
                          <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Converting...</>
                        ) : (
                          <><Code className="w-4 h-4 mr-2" />Convert</>
                        )}
                      </Button>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Output Section */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">BPMN Output</CardTitle>
                {bpmnXml && (
                  <Button onClick={downloadBpmn} size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {stats && (
                <div className="mb-4 p-3 bg-accent rounded-lg">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Tasks</p>
                      <p className="font-semibold text-foreground">{stats.tasks}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Gateways</p>
                      <p className="font-semibold text-foreground">{stats.gateways}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Flows</p>
                      <p className="font-semibold text-foreground">{stats.bpmn_flows}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="relative">
                {bpmnXml ? (
                  <pre className="font-mono text-xs bg-muted p-4 rounded-lg overflow-auto max-h-[400px] text-foreground">
                    {bpmnXml}
                  </pre>
                ) : (
                  <div className="bg-muted rounded-lg p-8 text-center min-h-[280px] flex flex-col items-center justify-center">
                    <Code className="w-12 h-12 text-muted-foreground mb-3" />
                    <p className="text-muted-foreground">BPMN output will appear here</p>
                  </div>
                )}
              </div>

              {(bpmnXml || sopText || uploadedFile) && (
                <div className="mt-4 flex justify-end">
                  <Button variant="outline" size="sm" onClick={clearAll}>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Clear All
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

export default App;
