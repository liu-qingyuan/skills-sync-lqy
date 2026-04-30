import React, { useCallback, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  type Edge,
  type Node,
  type NodeProps,
} from '@xyflow/react';

type EvidenceItem = string | { label?: string; path?: string; detail?: string };
type FlowNode = {
  id: string;
  type?: string;
  label: string;
  symbolId?: string;
  role?: string;
  file?: string;
  line?: number;
  position?: { x: number; y: number };
  width?: number;
  height?: number;
  evidence?: EvidenceItem[];
  rationale?: string;
};
type FlowEdge = {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  type?: string;
  label?: string;
  evidence?: EvidenceItem[];
  rationale?: string;
};
type FlowGraph = {
  id: string;
  title: string;
  summary?: string;
  nodes: FlowNode[];
  edges: FlowEdge[];
  layout?: Record<string, unknown>;
};
type FlowPayload = { version: number; graphs: FlowGraph[] };
type Selection = { kind: 'node' | 'edge'; item: FlowNode | FlowEdge } | null;

const TYPE_STYLE: Record<string, { color: string; stroke?: string; badge: string }> = {
  call: { color: '#315efb', badge: 'CALL' },
  ipc: { color: '#7c3aed', stroke: '6 4', badge: 'IPC' },
  data: { color: '#0f9f6e', badge: 'DATA' },
  error: { color: '#d97706', stroke: '3 5', badge: 'ERROR' },
  external: { color: '#dc2626', stroke: '8 4', badge: 'EXT' },
  test: { color: '#64748b', stroke: '2 4', badge: 'TEST' },
  default: { color: '#315efb', badge: 'EDGE' },
};

const POSITION_BY_HANDLE: Record<string, Position> = {
  top: Position.Top,
  right: Position.Right,
  bottom: Position.Bottom,
  left: Position.Left,
};

function evidenceLabel(item: EvidenceItem, index: number): string {
  if (typeof item === 'string') return item;
  return item.label || item.path || item.detail || `evidence-${index + 1}`;
}

function evidenceDetail(item: EvidenceItem): string | null {
  if (typeof item === 'string') return null;
  return item.detail || item.path || null;
}

function ArchitectureNode(props: NodeProps<Node<FlowNode>>) {
  const data = props.data;
  const nodeType = data.type || 'runtime';
  return (
    <div
      className={`af-node af-node-${nodeType}`}
      data-flow-node={props.id}
      data-node-type={nodeType}
      style={{ minWidth: data.width || 220, minHeight: data.height || 92 }}
    >
      {Object.entries(POSITION_BY_HANDLE).map(([id, position]) => (
        <Handle key={id} id={id} type="source" position={position} className={`af-handle af-handle-${id}`} />
      ))}
      {Object.entries(POSITION_BY_HANDLE).map(([id, position]) => (
        <Handle key={`target-${id}`} id={id} type="target" position={position} className={`af-handle af-handle-${id}`} />
      ))}
      <div className="af-node-type">{nodeType}</div>
      <div className="af-node-label">{data.label}</div>
      <div className="af-node-evidence">{(data.evidence || []).length} evidence refs</div>
    </div>
  );
}

function EvidencePanel({ selection, graph }: { selection: Selection; graph: FlowGraph }) {
  const item = selection?.item;
  return (
    <aside className="af-evidence-panel" data-testid="architecture-flow-evidence-panel">
      <div className="af-panel-kicker">Click-to-evidence</div>
      {item ? (
        <>
          <h4>{selection?.kind === 'edge' ? 'Edge' : 'Node'} · {'label' in item ? item.label : item.id}</h4>
          <p><strong>ID:</strong> <code>{item.id}</code></p>
          {'symbolId' in item && item.symbolId ? <p><strong>Symbol ID:</strong> <code>{item.symbolId}</code></p> : null}
          {'file' in item && item.file ? <p><strong>Source:</strong> <code>{item.file}{'line' in item && item.line ? `:${item.line}` : ''}</code></p> : null}
          {'type' in item && item.type ? <p><strong>Type:</strong> <span className="af-chip">{item.type}</span></p> : null}
          {'source' in item ? <p><strong>Route:</strong> <code>{item.source}</code> → <code>{item.target}</code></p> : null}
          <ul>
            {(item.evidence || []).map((evidence, index) => (
              <li key={`${item.id}-${index}`}>
                <span>{evidenceLabel(evidence, index)}</span>
                {evidenceDetail(evidence) ? <small>{evidenceDetail(evidence)}</small> : null}
              </li>
            ))}
          </ul>
          {item.rationale ? <p className="af-rationale">Fallback rationale: {item.rationale}</p> : null}
        </>
      ) : (
        <>
          <h4>{graph.title}</h4>
          <p>Click a node or edge to inspect source/GitNexus evidence. The payload is embedded in this page for file:// use.</p>
        </>
      )}
    </aside>
  );
}

function ArchitectureFlow({ graph }: { graph: FlowGraph }) {
  const [selection, setSelection] = useState<Selection>(null);
  const nodeTypes = useMemo(() => ({ architecture: ArchitectureNode }), []);
  const initialNodes = useMemo<Node<FlowNode>[]>(() => graph.nodes.map((node) => ({
    id: node.id,
    type: 'architecture',
    position: node.position || { x: 0, y: 0 },
    width: node.width || 220,
    height: node.height || 92,
    data: node,
  })), [graph]);
  const initialEdges = useMemo<Edge[]>(() => graph.edges.map((edge) => {
    const style = TYPE_STYLE[edge.type || 'default'] || TYPE_STYLE.default;
    return {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      sourceHandle: edge.sourceHandle,
      targetHandle: edge.targetHandle,
      label: edge.label,
      type: 'smoothstep',
      markerEnd: { type: MarkerType.ArrowClosed, color: style.color },
      style: { stroke: style.color, strokeWidth: 2.4, strokeDasharray: style.stroke },
      labelStyle: { fill: style.color, fontWeight: 700, fontSize: 12 },
      labelBgStyle: { fill: 'rgba(255,255,255,.92)' },
      data: { semanticType: edge.type, badge: style.badge, evidence: edge.evidence },
      ariaLabel: `architecture edge ${edge.id}: ${edge.label || edge.type || 'edge'}`,
    } satisfies Edge;
  }), [graph]);
  const [nodes, _setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, _setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const handleNodeClick = useCallback((_event: React.MouseEvent, node: Node<FlowNode>) => {
    setSelection({ kind: 'node', item: node.data });
  }, []);
  const handleEdgeClick = useCallback((_event: React.MouseEvent, edge: Edge) => {
    const source = graph.edges.find((candidate) => candidate.id === edge.id);
    if (source) setSelection({ kind: 'edge', item: source });
  }, [graph.edges]);
  return (
    <div className="af-shell" data-graph-id={graph.id}>
      <div className="af-canvas" role="application" aria-label={`${graph.title} interactive architecture graph`}>
        <ReactFlowProvider>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            onEdgeClick={handleEdgeClick}
            fitView
            fitViewOptions={{ padding: 0.18 }}
            nodesDraggable
            panOnDrag
            zoomOnScroll
            zoomOnPinch
            elementsSelectable
            proOptions={{ hideAttribution: true }}
          >
            <Background gap={22} size={1} />
            <MiniMap pannable zoomable nodeStrokeWidth={3} />
            <Controls showInteractive />
          </ReactFlow>
        </ReactFlowProvider>
      </div>
      <EvidencePanel selection={selection} graph={graph} />
    </div>
  );
}

function parsePayload(): FlowPayload | null {
  const script = document.querySelector<HTMLScriptElement>('script[type="application/json"][data-architecture-flow]');
  if (!script || !script.textContent) return null;
  try {
    return JSON.parse(script.textContent) as FlowPayload;
  } catch (error) {
    console.error('Failed to parse architecture-flow payload', error);
    return null;
  }
}

function mountFunctionInventories() {
  const tables = Array.from(document.querySelectorAll<HTMLTableElement>('table[data-function-inventory]'));
  tables.forEach((table) => {
    const scope = table.closest<HTMLElement>('[data-function-inventory-scope]') || table.parentElement || document.body;
    const input = scope.querySelector<HTMLInputElement>('[data-function-inventory-search]');
    const status = scope.querySelector<HTMLElement>('[data-function-inventory-count]');
    const rows = Array.from(table.tBodies[0]?.rows || []);
    const pageSize = Math.max(1, Number(table.dataset.pageSize || '50') || 50);
    let page = 0;
    let controls = scope.querySelector<HTMLElement>('[data-function-inventory-controls]');
    if (!controls) {
      controls = document.createElement('div');
      controls.className = 'function-inventory-controls';
      controls.dataset.functionInventoryControls = 'true';
      controls.innerHTML = '<button type="button" data-function-page="prev">上一页</button><span data-function-page-status></span><button type="button" data-function-page="next">下一页</button>';
      table.insertAdjacentElement('afterend', controls);
    }
    const prev = controls.querySelector<HTMLButtonElement>('[data-function-page="prev"]');
    const next = controls.querySelector<HTMLButtonElement>('[data-function-page="next"]');
    const pageStatus = controls.querySelector<HTMLElement>('[data-function-page-status]');
    const apply = () => {
      const query = (input?.value || '').trim().toLowerCase();
      const matched = rows.filter((row) => !query || row.textContent?.toLowerCase().includes(query));
      const totalPages = Math.max(1, Math.ceil(matched.length / pageSize));
      page = Math.min(page, totalPages - 1);
      const start = page * pageSize;
      const visible = new Set(matched.slice(start, start + pageSize));
      rows.forEach((row) => { row.hidden = !visible.has(row); });
      if (status) status.textContent = `显示 ${matched.length} / ${rows.length} 个函数；每页 ${pageSize} 行`;
      if (pageStatus) pageStatus.textContent = `${page + 1} / ${totalPages}`;
      if (prev) prev.disabled = page <= 0;
      if (next) next.disabled = page >= totalPages - 1;
      table.dataset.filteredRows = String(matched.length);
    };
    input?.addEventListener('input', () => { page = 0; apply(); });
    prev?.addEventListener('click', () => { page = Math.max(0, page - 1); apply(); });
    next?.addEventListener('click', () => { page += 1; apply(); });
    apply();
  });
}

function mountAll() {
  mountFunctionInventories();
  const payload = parsePayload();
  const containers = Array.from(document.querySelectorAll<HTMLElement>('[data-flow-graph]'));
  if (!payload) {
    containers.forEach((container) => { container.innerHTML = '<p class="af-error">Missing embedded architecture-flow payload.</p>'; });
    return;
  }
  containers.forEach((container) => {
    const graphId = container.dataset.flowGraph;
    const graph = payload.graphs.find((candidate) => candidate.id === graphId) || payload.graphs[0];
    if (!graph) {
      container.innerHTML = '<p class="af-error">No architecture-flow graph found.</p>';
      return;
    }
    createRoot(container).render(<ArchitectureFlow graph={graph} />);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', mountAll);
} else {
  mountAll();
}
