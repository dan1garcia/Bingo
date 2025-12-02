// public/js/board.js
document.addEventListener('DOMContentLoaded', function(){
  const grid = document.getElementById('boardGrid');
  const current = document.getElementById('currentNumber');
  const drawnList = document.getElementById('drawnList');
  const drawBtn = document.getElementById('drawNumberBtn');

  // generar tablero 1..100 (10x10)
  if (grid){
    for (let i=1;i<=100;i++){
      const cell = document.createElement('div');
      cell.className = 'board-cell';
      cell.textContent = i;
      cell.tabIndex = 0;
      cell.addEventListener('click', ()=> cell.classList.toggle('marked'));
      grid.appendChild(cell);
    }
  }

  // lógica simple de sorteo en cliente (solo demo)
  let drawn = [];
  function updateDrawn(){
    if(!drawn.length){ drawnList.textContent = 'Aún no se han sorteado números'; return; }
    drawnList.innerHTML = drawn.map(n=> `<span style="display:inline-block;margin:4px;padding:6px 8px;background:#f1f6f9;border-radius:8px">${n}</span>`).join('');
  }

  if (drawBtn){
    drawBtn.addEventListener('click', ()=>{
      if (drawn.length >= 100) return;
      let n;
      do{ n = Math.floor(Math.random()*100)+1 } while(drawn.includes(n));
      drawn.push(n);
      if (current) current.textContent = n;
      updateDrawn();
    });
  }
});
