// Compact projection for the repo's JavaScript storyworld_reader.html.
// The reader dispatches on pointer_type/operator_type and applies the same Nudge
// semantics without script_element_type or explicit coefficient: 1 metadata.
// The full Sweepweave/Storytron metadata export remains available from
// build_sweepweave.mjs for downstream consumers that need those fields.
export function compactSweepweave(full){
  function visit(node){
    if(Array.isArray(node))return node.map(visit);
    if(!node||typeof node!=='object')return node;
    const out={};
    for(const [key,value] of Object.entries(node)){
      if(key==='script_element_type')continue;
      if(key==='coefficient' && node.pointer_type==='Bounded Number Pointer' && value===1)continue;
      out[key]=visit(value);
    }
    return out;
  }
  return visit(full);
}
