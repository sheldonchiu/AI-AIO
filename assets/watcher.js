import { refs } from "/utils/state"
/**
 * Returns an array of objects containing the names and current values of all
 * matching refs, optionally filtering by prefix and/or refs to update.
 *
 * @param {Array} [var_list=null] - An optional array of ref names to update.
 * @param {string} [prefix=null] - An optional prefix to match for ref names.
 *
 * @returns {Array} - An array of objects containing ref names and current values.
 */
export const getRefValues = (refs_to_update=[], prefix=null) => {
    const refValues = [];
  
    // Loop through each ref entry using Object.entries
    Object.entries(refs).forEach(([refName, ref]) => {
      // Initialize value variable
      let value;
      
      // If the ref.current is null, move on to the next ref
      if (ref.current === null) {
        return;
      }
      
      // Check if prefix is provided and if the refName starts with the prefix
      else if (!prefix || refName.startsWith(prefix)) {
        // If refs_to_update is provided, check if the refName is in the array
        if (refs_to_update.length > 0 && !refs_to_update.includes(refName)) {
          return;
        }
        // Otherwise, switch on the ref.current.type to get the current value
        switch (ref.current.type) {
          case "checkbox":
            value = ref.current.checked;
            break;
          case "radio":
            value = ref.current.checked;
            break;
          case "select-multiple":
            value = Array.from(ref.current.selectedOptions, (option) => option.value);
            break;
          default:
            value = ref.current.value;
            break;
        }
        refValues.push({ refName, value });
      }
    });
  
    return refValues;
  };
  
  export const updateRefValues = (base_state, ref_mapping, rendering=false) => {
    let variableValue;
  
    Object.entries(refs).forEach(([refName, ref]) => {
  
      function setValue(){
        if(typeof variableValue === "string") {
          ref.current.value = variableValue;
        }
        else if(typeof variableValue === "boolean") {
            if(!rendering) {
              if(ref.current.checked != variableValue){
                ref.current.click();
              }
            }
            else{
              ref.current.checked = variableValue;
            }
        }
      };
  
      if (ref.current === null) {
        return;
      } 
      else {
          const parts = refName.split("__");
          if (parts.length === 2) {
            try{
              if (!(parts[1] in ref_mapping)) {
                return;
              }
              variableValue = eval(ref_mapping[parts[1]]);
              setValue();
            } catch (error) {
              console.error(`Failed to decode and insert env ${key} ${value}`);
            }
          }
          // If there are three parts, assume it's a dictionary and return the second and third parts as a tuple
          else if (parts.length === 3) {
              try {
                  if (!(parts[1] in ref_mapping)) {
                      return;
                  }
                  variableValue = eval(ref_mapping[parts[1]]);
                  variableValue = variableValue[Object.keys(variableValue)[parseInt(parts[2])]];
                  setValue();
              } catch (error) {
                  console.error(`Failed to decode and insert env ${key} ${value}`);
              }
          }
      }
  
    });
  };