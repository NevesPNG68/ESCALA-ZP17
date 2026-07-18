(async()=>{
  const wait=milliseconds=>new Promise(resolve=>setTimeout(resolve,milliseconds));

  async function fetchText(url,label){
    let lastError;
    for(let attempt=1;attempt<=3;attempt++){
      try{
        const response=await fetch(url,{cache:"no-store"});
        if(response.ok)return response.text();
        lastError=new Error(`${label} indisponível (HTTP ${response.status})`);
      }catch(error){
        lastError=error;
      }
      if(attempt<3)await wait(400*attempt);
    }
    throw lastError||new Error(`${label} indisponível`);
  }

  try{
    const manifestText=await fetchText("vendor/xlsx.parts/manifest.txt","manifesto do leitor Excel");
    const manifest=manifestText.trim().split(/\s+/);
    const count=Number(manifest[0]);
    if(!Number.isInteger(count)||count<1)throw new Error("manifesto do leitor Excel inválido");

    const parts=[];
    for(let index=0;index<count;index++){
      const filename=`part-${String(index).padStart(3,"0")}.txt`;
      parts.push(await fetchText(`vendor/xlsx.parts/${filename}`,`parte ${index+1}`));
    }

    const binary=atob(parts.join(""));
    const bytes=Uint8Array.from(binary,character=>character.charCodeAt(0));
    (0,eval)(new TextDecoder().decode(bytes));
    if(!window.XLSX)throw new Error("biblioteca Excel não inicializada");
    window.dispatchEvent(new Event("xlsx-ready"));
  }catch(error){
    window.dispatchEvent(new CustomEvent("xlsx-error",{detail:error}));
  }
})();
