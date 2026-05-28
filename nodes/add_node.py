# ADR-051 (amended 2026-05-27) / EPIC-SAF-003: AddNode is the seed
# flow's only authored node. Mutation-capable. Emits a MutationBatch
# that adds axiom-official/identity-demo's Identity node + the edge
# AddNode→Identity.
#
# The amended ADR-051 resume-from-emitter semantics make this work
# cleanly: after the parent's worker dispatches AddNode and processes
# its MutationBatch, the child execution resumes at AddNode's
# outgoing edges (NOT at the graph's start_node). The new edge to
# Identity fires immediately, Identity runs (passthrough), flow
# COMPLETED. AddNode never re-runs in the child — no idempotency
# tracking needed.
"""AddNode — the bootstrap node that mutates the flow into a 2-node graph."""
from __future__ import annotations

from gen.axiom_official_mutation_demo_messages_messages_pb2 import Pulse
from gen.axiom_context import AxiomContext


# The single mutation_capable node in axiom-official/identity-demo is
# Identity. The v1 ADR-051 resolver picks it by virtue of the "one
# mutation_capable per package" invariant — we don't need to (and
# can't) name it explicitly here.
ADDED_PACKAGE = "axiom-official/identity-demo"
ADDED_PACKAGE_VERSION = "0.1.0"


def add_node(ax: AxiomContext, input: Pulse) -> Pulse:
    try:
        new_iid = ax.mutation.flow.add_node(
            package=ADDED_PACKAGE,
            version=ADDED_PACKAGE_VERSION,
        )
        pos = ax.reflection.flow.position
        ax.mutation.flow.add_edge(
            src_instance=pos.current_instance,
            dst_instance=new_iid,
        )
        ax.log.info(
            "AddNode emitted MutationBatch",
            src_instance=pos.current_instance,
            new_iid=new_iid,
        )
    except Exception as exc:  # noqa: BLE001
        ax.log.error("AddNode mutation buffer failed", error=str(exc))

    # Pass the Pulse through unchanged — the resume-from-emitter
    # dispatch on the child execution carries this output into the
    # newly-added Identity edge as its input.
    out = Pulse()
    out.text = input.text
    return out


__all__ = ["add_node", "ADDED_PACKAGE", "ADDED_PACKAGE_VERSION"]
