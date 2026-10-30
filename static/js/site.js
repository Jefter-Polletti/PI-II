(() => {
 const byId=id=>document.getElementById(id), keys=['product_id','width_cm','height_cm','quantity','material','finish'];
 const data=()=>Object.fromEntries(keys.map(k=>[k,byId(k).value]));
 const sync=()=>{for(const [k,v] of Object.entries(data()))document.querySelector(`#quote-form input[name="${k}"]`).value=v};
 const csrf=()=>document.querySelector('[name="csrfmiddlewaretoken"]').value;
 byId('calculate').addEventListener('click',async()=>{
   sync();byId('result').textContent='Calculando...';
   try {const res=await fetch('/api/v1/calcular-preco/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf()},body:JSON.stringify(data())});
      const j=await res.json();byId('result').textContent=res.ok?`Total estimado: R$ ${j.total} (unitário: R$ ${j.unit_price})`:(j.error||'Não foi possível calcular.');
   }catch(e){byId('result').textContent='Não foi possível acessar o servidor.'}
 });
 byId('quote-form').addEventListener('submit',sync);
 byId('zipcode').addEventListener('blur',async()=>{
    const cep=byId('zipcode').value.replace(/\D/g,'');if(cep.length!==8)return;
    try{const res=await fetch(`https://viacep.com.br/ws/${cep}/json/`);if(!res.ok)return;const j=await res.json();if(j.erro)return;
      for(const [id,key] of [['street','logradouro'],['neighborhood','bairro'],['city','localidade'],['state','uf']])byId(id).value=j[key]||'';
    }catch(e){}
 });
})();
