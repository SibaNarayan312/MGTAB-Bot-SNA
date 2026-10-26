import React, { useEffect, useRef, useState, useCallback } from 'react';
import cytoscape, { Core, EventObject } from 'cytoscape';
import {
  NetworkGraphData,
  GraphNodeData,
  GraphEdgeData,
  GraphLayoutAlgorithm,
} from '../../types/network';
import { getCytoscapeStylesheet, getLayoutConfig } from '../../utils/cytoscapeConfig';
import { GraphControls } from './GraphControls';
import { GraphLegend } from './GraphLegend';
import { NodeDetailsPanel } from './NodeDetailsPanel';
import { EdgeDetailsPanel } from './EdgeDetailsPanel';
import { LoadingSkeleton } from '../common/LoadingSkeleton';
import { EmptyState } from '../common/EmptyState';
import { Network as NetIcon } from 'lucide-react';

interface NetworkGraphProps {
  data: NetworkGraphData | null;
  loading?: boolean;
  onNodeSelect?: (node: GraphNodeData | null) => void;
  height?: string;
  showControls?: boolean;
  showLegend?: boolean;
  showDetailsPanel?: boolean;
  initialLayout?: GraphLayoutAlgorithm;
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  data,
  loading = false,
  onNodeSelect,
  height = '620px',
  showControls = true,
  showLegend = true,
  showDetailsPanel = true,
  initialLayout = 'cose',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  const [layoutAlgorithm, setLayoutAlgorithm] = useState<GraphLayoutAlgorithm>(initialLayout);
  const layoutAlgorithmRef = useRef<GraphLayoutAlgorithm>(initialLayout);
  useEffect(() => {
    layoutAlgorithmRef.current = layoutAlgorithm;
  }, [layoutAlgorithm]);

  const [selectedNode, setSelectedNode] = useState<GraphNodeData | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdgeData | null>(null);

  // Stable callback ref to prevent Cytoscape re-creation when parent re-renders
  const onNodeSelectRef = useRef(onNodeSelect);
  useEffect(() => {
    onNodeSelectRef.current = onNodeSelect;
  }, [onNodeSelect]);

  // Clean destruction of previous Cytoscape instance
  const destroyCytoscape = useCallback(() => {
    if (cyRef.current) {
      try {
        cyRef.current.stop();
        cyRef.current.removeAllListeners();
        cyRef.current.destroy();
      } catch (err) {
        console.warn('[NetworkGraph] Error during Cytoscape teardown:', err);
      }
      cyRef.current = null;
    }
  }, []);

  // Initialize and Render Cytoscape Graph with defensive limits
  const renderGraph = useCallback(() => {
    if (!containerRef.current || !data || data.nodes.length === 0) return;

    // Cleanup previous instance before instantiating a new one
    destroyCytoscape();

    // Defensive capping: max 200 nodes and 400 edges
    const safeNodes = data.nodes.slice(0, 200);
    const safeNodeIdSet = new Set(safeNodes.map((n) => String(n.id)));
    const safeEdges = data.edges
      .filter((e) => safeNodeIdSet.has(String(e.source)) && safeNodeIdSet.has(String(e.target)))
      .slice(0, 400);

    // Convert to Cytoscape format
    const elements: cytoscape.ElementDefinition[] = [
      ...safeNodes.map((node) => ({
        group: 'nodes' as const,
        data: {
          id: String(node.id),
          label: node.label || `User ${node.id}`,
          screen_name: node.screen_name,
          prediction: node.prediction || 'UNKNOWN',
          probability: node.probability,
          community_id: node.community_id,
          degree: node.degree || 10,
          pagerank: node.pagerank || 0.001,
          clustering: node.clustering,
          is_seed: Boolean(node.is_seed),
        },
      })),
      ...safeEdges.map((edge, idx) => ({
        group: 'edges' as const,
        data: {
          id: edge.id || `e-${edge.source}-${edge.target}-${idx}`,
          source: String(edge.source),
          target: String(edge.target),
          relationship: edge.relationship || 'FOLLOW',
          weight: edge.weight || 1,
        },
      })),
    ];

    try {
      // Create Cytoscape instance
      const cy = cytoscape({
        container: containerRef.current,
        elements,
        style: getCytoscapeStylesheet(),
        layout: getLayoutConfig(layoutAlgorithmRef.current),
        minZoom: 0.15,
        maxZoom: 3.5,
        wheelSensitivity: 0.25,
        boxSelectionEnabled: false,
      });

      // Node click handler using stable ref
      cy.on('tap', 'node', (evt: EventObject) => {
        const nodeData = evt.target.data() as GraphNodeData;
        setSelectedNode(nodeData);
        setSelectedEdge(null);
        onNodeSelectRef.current?.(nodeData);
      });

      // Edge click handler
      cy.on('tap', 'edge', (evt: EventObject) => {
        const edgeData = evt.target.data() as GraphEdgeData;
        setSelectedEdge(edgeData);
        setSelectedNode(null);
      });

      // Background click handler
      cy.on('tap', (evt: EventObject) => {
        if (evt.target === cy) {
          setSelectedNode(null);
          setSelectedEdge(null);
          onNodeSelectRef.current?.(null);
        }
      });

      cyRef.current = cy;
    } catch (err) {
      console.error('[NetworkGraph] Failed to initialize Cytoscape instance:', err);
    }
  }, [data, destroyCytoscape]);

  // Re-render only when data changes
  useEffect(() => {
    renderGraph();

    return () => {
      destroyCytoscape();
    };
  }, [renderGraph, destroyCytoscape]);

  // Graph control handlers
  const handleZoomIn = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 1.25);
    }
  };

  const handleZoomOut = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 0.8);
    }
  };

  const handleFit = () => {
    if (cyRef.current) {
      cyRef.current.fit(undefined, 40);
    }
  };

  const handleResetLayout = () => {
    if (cyRef.current) {
      cyRef.current.stop();
      const layout = cyRef.current.layout(getLayoutConfig(layoutAlgorithm));
      layout.run();
    }
  };

  const handleLayoutChange = (newLayout: GraphLayoutAlgorithm) => {
    setLayoutAlgorithm(newLayout);
    layoutAlgorithmRef.current = newLayout;
    if (cyRef.current) {
      cyRef.current.stop();
      const layout = cyRef.current.layout(getLayoutConfig(newLayout));
      layout.run();
    }
  };

  if (loading) {
    return (
      <div
        style={{ height }}
        className="w-full rounded-xl border border-slate-800 bg-slate-950/80 flex items-center justify-center p-6"
      >
        <div className="w-full h-full space-y-3">
          <div className="flex justify-between items-center">
            <LoadingSkeleton className="h-6 w-48" />
            <LoadingSkeleton className="h-8 w-64" />
          </div>
          <LoadingSkeleton className="h-[calc(100%-3rem)] w-full rounded-xl" />
        </div>
      </div>
    );
  }

  if (!data || data.nodes.length === 0) {
    return (
      <div
        style={{ height }}
        className="w-full rounded-xl border border-slate-800 bg-slate-950/80 flex items-center justify-center"
      >
        <EmptyState
          icon={NetIcon}
          title="No Network Graph Data"
          description="There are no nodes or edges to display with the current filter parameters."
        />
      </div>
    );
  }

  return (
    <div
      style={{ height }}
      className="relative w-full rounded-xl border border-slate-800 bg-slate-950 overflow-hidden shadow-2xl graph-canvas-grid select-none"
    >
      {/* Cytoscape Container Element */}
      <div ref={containerRef} className="w-full h-full cytoscape-container" />

      {/* Top Left Controls */}
      {showControls && (
        <div className="absolute top-4 left-4 z-10">
          <GraphControls
            onZoomIn={handleZoomIn}
            onZoomOut={handleZoomOut}
            onFit={handleFit}
            onReset={handleResetLayout}
            currentLayout={layoutAlgorithm}
            onLayoutChange={handleLayoutChange}
          />
        </div>
      )}

      {/* Bottom Left Legend */}
      {showLegend && (
        <div className="absolute bottom-4 left-4 z-10 max-w-xs">
          <GraphLegend />
        </div>
      )}

      {/* Node Details Inspector */}
      {showDetailsPanel && selectedNode && (
        <NodeDetailsPanel node={selectedNode} onClose={() => setSelectedNode(null)} />
      )}

      {/* Edge Details Inspector */}
      {showDetailsPanel && selectedEdge && (
        <EdgeDetailsPanel edge={selectedEdge} onClose={() => setSelectedEdge(null)} />
      )}

      {/* Node/Edge Count Watermark */}
      <div className="absolute bottom-3 right-4 z-10 text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-800 backdrop-blur-sm">
        <span>Nodes: {data.nodes.length}</span>
        <span className="mx-1.5">&bull;</span>
        <span>Edges: {data.edges.length}</span>
        {data.metadata?.seed_node && (
          <>
            <span className="mx-1.5">&bull;</span>
            <span className="text-amber-400">Seed: {data.metadata.seed_node}</span>
          </>
        )}
      </div>
    </div>
  );
};
