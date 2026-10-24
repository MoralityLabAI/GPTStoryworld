// Compact, behavior-equivalent projection for this repo's JavaScript reader.
// Full Sweepweave script metadata stays available through build_sweepweave.mjs.
// JS evaluator uses pointer_type/operator_type and an implicit coefficient of 1.
export function compactSweepweave(full){
  function visit(node){
    if(Array.isArray(node))return node.map(visit);
    if(!node||typeof node!=='object')return node;
    const out={};
    for(const [key,value] of Object.entries(node)){
      if(key==='script_element_type')continue;
      if(key==='coefficient' && node.pointer_type==='Bounded Number Pointer' && value===1)continue;
      // Reaction branches use complementary conditions weighted 20 versus 0.
      // Smaller boolean comparator returns 1 versus 0 and chooses the same
      // reaction under every state, including the exact threshold boundary.
      if(key==='desirability_script' && typeof node.consequence_id==='string' &&
          value?.operator_type==='Addition'){
        const first=value.operands?.[0];
        if(first?.operator_type==='Multiplication' &&
            first.operands?.[0]?.operator_type==='Arithmetic Comparator' &&
            first.operands?.[1]?.pointer_type==='Bounded Number Constant' &&
            first.operands[1].value===20){
          out[key]=visit(first.operands[0]);
          continue;
        }
      }
      out[key]=visit(value);
    }
    return out;
  }
  return visit(full);
}
