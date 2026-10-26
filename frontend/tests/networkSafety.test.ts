import assert from 'node:assert';
import { normalizeGraphData } from '../src/utils/graphNormalizer.ts';

console.log('--- Running Network Safety & Bounding Verification Tests ---');

// Test 1: Null/empty payload returns safe empty graph structure
{
  const emptyRes = normalizeGraphData(null);
  assert.strictEqual(emptyRes.nodes.length, 0);
  assert.strictEqual(emptyRes.edges.length, 0);
  assert.strictEqual(emptyRes.metadata?.total_nodes, 0);
  console.log('✓ Test 1: Null/empty payload returns safe empty graph structure');
}

// Test 2: Massive graph clamping (prevent browser freeze with 5,000 nodes and 50,000 edges)
{
  const massiveRaw = {
    nodes: Array.from({ length: 5000 }, (_, i) => ({
      id: i,
      label: `User ${i}`,
      bot_label: i % 2 === 0 ? 1 : 0,
      degree: 100,
    })),
    edges: Array.from({ length: 50000 }, (_, i) => ({
      source: i % 300,
      target: (i + 1) % 300,
      relationship_type: 'followers',
      weight: 1.5,
    })),
    metadata: {
      total_nodes: 10199,
      total_edges: 1700108,
      is_filtered: true,
    },
  };

  const bounded = normalizeGraphData(massiveRaw);

  // Must clamp nodes <= 200
  assert.ok(
    bounded.nodes.length <= 200,
    `Nodes must be capped to <= 200 for Cytoscape UI performance, got: ${bounded.nodes.length}`
  );
  assert.strictEqual(bounded.nodes.length, 200);

  // Must clamp edges <= 400
  assert.ok(
    bounded.edges.length <= 400,
    `Edges must be capped to <= 400 for Cytoscape UI performance, got: ${bounded.edges.length}`
  );

  // Must only include edges between the 200 valid nodes
  const validNodeIds = new Set(bounded.nodes.map((n) => n.id));
  for (const edge of bounded.edges) {
    assert.ok(validNodeIds.has(edge.source), `Source ${edge.source} must exist in bounded nodes`);
    assert.ok(validNodeIds.has(edge.target), `Target ${edge.target} must exist in bounded nodes`);
  }

  // Must normalize string IDs and types
  assert.strictEqual(typeof bounded.nodes[0].id, 'string');
  assert.strictEqual(typeof bounded.edges[0].source, 'string');
  assert.strictEqual(typeof bounded.edges[0].target, 'string');

  // Must convert bot_label 1 -> 'BOT', 0 -> 'HUMAN'
  assert.strictEqual(bounded.nodes[0].prediction, 'BOT');
  assert.strictEqual(bounded.nodes[1].prediction, 'HUMAN');

  // Must normalize relationship to uppercase
  assert.strictEqual(bounded.edges[0].relationship, 'FOLLOWERS');

  console.log('✓ Test 2: Massive 5,000-node / 50,000-edge payload safely clamped to 200 nodes / <= 400 edges');
}

// Test 3: Relationship mapping and string preservation
{
  const testData = {
    nodes: [
      { id: 10, label: 'Alice', bot_label: 0 },
      { id: 20, label: 'BobBot', bot_label: 1 },
    ],
    edges: [
      { source: 10, target: 20, relationship_type: 'friends', weight: 2.0 },
    ],
  };

  const res = normalizeGraphData(testData);
  assert.strictEqual(res.nodes.length, 2);
  assert.strictEqual(res.nodes[0].id, '10');
  assert.strictEqual(res.nodes[0].prediction, 'HUMAN');
  assert.strictEqual(res.nodes[1].id, '20');
  assert.strictEqual(res.nodes[1].prediction, 'BOT');

  assert.strictEqual(res.edges.length, 1);
  assert.strictEqual(res.edges[0].source, '10');
  assert.strictEqual(res.edges[0].target, '20');
  assert.strictEqual(res.edges[0].relationship, 'FRIENDS');
  assert.strictEqual(res.edges[0].weight, 2.0);

  console.log('✓ Test 3: Node predictions, IDs, and edge relationship types normalized correctly');
}

console.log('--- All Network Safety Verification Tests Passed Successfully! ---');
