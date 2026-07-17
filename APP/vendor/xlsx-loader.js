(async()=>{
  try{
    const manifest=(await (await fetch("vendor/xlsx.parts/manifest.txt",{cache:"no-store"})).text()).trim().split(/\s+/);
    const count=Number(manifest[0]);
    if(!Number.isInteger(count)||count<1)throw new Error("manifesto do leitor Excel inválido");
    const parts=await Promise.all(Array.from({length:count},(_,index)=>fetch(`vendor/xlsx.parts/part-${String(index).padStart(3,"0")}.txt`).then(response=>{
      if(!response.ok)throw new Error(`parte ${index+1} indisponível`);
      return response.text();
    })));
    const binary=atob(parts.join(""));
    const bytes=Uint8Array.from(binary,character=>character.charCodeAt(0));
    (0,eval)(new TextDecoder().decode(bytes));
    if(!window.XLSX)throw new Error("biblioteca Excel não inicializada");
    window.dispatchEvent(new Event("xlsx-ready"));
  }catch(error){
    window.dispatchEvent(new CustomEvent("xlsx-error",{detail:error}));
  }
})();
