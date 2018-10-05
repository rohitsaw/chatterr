document.addEventListener("DOMContentLoaded", ()=>{
  var socket=io.connect(location.protocol+'//'+document.domain+':'+location.port+'/sessionroom');
  document.querySelector("#msgsend").disabled=true;
  document.querySelector('#msg').onkeyup=()=>{
    if (document.querySelector('#msg').value.length>0)
        document.querySelector("#msgsend").disabled=false;
    else {
      document.querySelector("#msgsend").disabled=true;
    }
  };
  document.querySelector("#msgsend").onclick=()=>{
  const msg=document.querySelector("#msg").value
  socket.emit("msg",{"msg":msg});
  };
  socket.on('msgsend',data=>{
    const li= document.createElement("li");
    li.innerHTML=`${data.name}: ${data.msg}`;
    document.querySelector("#msglist").append(li);
    document.querySelector("#msg").value='';
    document.querySelector("#msgsend").disabled=true;
    return false;
  });
});