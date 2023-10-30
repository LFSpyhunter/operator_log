/* ----------------- JS FOR SWITCH----------------------- */
function show_me(port) {
  const span = document.getElementById("ip-commut");
  const ip = span.textContent;
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/portinfo");
  xhr.setRequestHeader("Content-Type", "application/json");
  var data = JSON.stringify({ ip: ip, port: port });
  xhr.responseType = "json";
  xhr.send(data);
  var modal = document.getElementById("myModal");
  xhr.onload = function () {
    var result = xhr.response;
    var x = document.getElementById("tableInfoPort");
    x.innerHTML = "";
    var h = document.createElement("h5");
    x.appendChild(h);
    h.appendChild(document.createTextNode(`Информация о ${port} порте`));
    var table = document.createElement("table");
    table.setAttribute("class", "table table-sm table-striped");
    var tbody = document.createElement("tbody");
    for (var key in result) {
      var row = document.createElement("tr");
      var td1 = document.createElement("td");
      td1.setAttribute("style", "width:30%");
      td1.appendChild(document.createTextNode(key));
      var td2 = document.createElement("td");
      if (key == "Договор") {
        if (result[key] == "не найден") {
          td2.appendChild(document.createTextNode(result[key]));
        } else {
          var a = document.createElement("a");
          a.appendChild(document.createTextNode("Жмякай"));
          a.href = `http://192.168.255.251/index.php?id_aabon=${result[key]}`;
          a.setAttribute("target", "_blank");
          td2.appendChild(a);
        }
      } else {
        td2.appendChild(document.createTextNode(result[key]));
      }
      row.appendChild(td1);
      row.appendChild(td2);
      tbody.appendChild(row);
      table.appendChild(tbody);
      x.appendChild(table);
    }
    modal.style.display = "block";
  };
  var span_close = document.getElementsByClassName("close")[0];
  span_close.onclick = function () {
    modal.style.display = "none";
  };
  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
}

function set_port(port) {
  const span = document.getElementById("ip-commut");
  const ip = span.textContent;
  var modal = document.getElementById("myModal");
  var x = document.getElementById("tableInfoPort");
  x.innerHTML = `<h5>Настройка ${port} порта </b></h5>
  <div class="set-port">
    <form method="post" action="/setport">
        <table class="table table-sm table-striped">
            <tbody>
                <tr>
                    <td>Порт 
                    <input name="port" type="hidden" value="${port}">
                    <input name="ip" type="hidden" value="${ip}"></td>
                    <td><select name="set_port" ">
                            <option value=""></option>
                            <option value="en">Включить</option>
                            <option value="dis">Выключить</option>
                        </select></td>
                    <td></td>
                </tr>
                <tr>
                    <td>Vlan</td>
                    <td> <select name="set_vlan">
                            <option value="add">Добавить</option>
                            <option value="del">Удалить</option>
                        </select></td>
                    <td> <input name="id_vlan" " placeholder="Введите vlan"></td>
                </tr>
                <tr>
                    <td>Описание</td>
                    <td><input name="descrip"></td>
                    <td></td>
                </tr>
                <tr>
                    <td>ACL</td>
                    <td><select name="set_acl">
                            <option value="add">Добавить</option>
                            <option value="del">Удалить</option>
                        </select></td>
                    <td><input  name="acl" placeholder="Введите ACL"></td>
                </tr>
            </tbody>
            
        </table>
        <div style="text-align: right;">
        <button type="submit" class="btn btn-dark">Применить</button>
        </div>
    </form>
</div>`;
  modal.style.display = "block";
  var span_close = document.getElementsByClassName("close")[0];
  span_close.onclick = function () {
    modal.style.display = "none";
  };
  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
}

function add_news() {
  var modal = document.getElementById("myModal");
  var x = document.getElementById("tableInfoPort");
  x.innerHTML = `<h5>Добавление новости</h5>
  <div clsss="add_news">
    <form method="post" action="">
        <span>Заголовок</span>
        <input class="add_title_news" type="text" required>
        <span>Описание новости</spane>
        <textarea rows="5" class="add_descrip_news" name="descrip"></textarea>
        <div style="text-align: right;">
        <button type="submit" class="btn btn-dark">Добавить</button>
        </div>
    </form>
</div>`;
  modal.style.display = "block";
  var span_close = document.getElementsByClassName("close")[0];
  span_close.onclick = function () {
    modal.style.display = "none";
  };
  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
}

// function user_settings(user) {
//   var xhr = new XMLHttpRequest();
//   xhr.open("GET", "/getsettings");
//   xhr.responseType = "json";
//   xhr.send(null);
//   // xhr.open("POST", "/getsettings");
//   // xhr.setRequestHeader("Content-Type", "application/json");
//   // var data = JSON.stringify({ user: user });
//   // xhr.responseType = "json";
//   // console.log(data);
//   // xhr.send(data);
//   var modal = document.getElementById("myModal");
//   xhr.onload = function () {
//     var result = xhr.response;
//     post_total = result["posts_kol"];
//     var x = document.getElementById("tableInfoPort");
//     x.innerHTML = `<h5>Настройки пользователя <span style="color: #ef7f1a">${user}</span></h5>
//       <div class="user_settings">
//         <form method="post" action="/setsettings">
//           <span>Количество выводимых записей</span>
//           <input style="width: 30px;" type="text" name="kolvo" value="${post_total}" required>
//           <div style="text-align: right; margin-top: 10px">
//               <button type="submit" class="btn btn-dark">Сохранить</button>
//           </div>
//         </form>
//       </div>`;
//   };
//   modal.style.display = "block";
//   var span_close = document.getElementsByClassName("close")[0];
//   span_close.onclick = function () {
//     modal.style.display = "none";
//   };
//   window.onclick = function (event) {
//     if (event.target == modal) {
//       modal.style.display = "none";
//     }
//   };
// }

function settings_user() {
  var set_user = document.getElementById("user_settings");
  if (set_user.style.display == "none") {
    set_user.style.display = "block";
  } else {
    set_user.style.display = "none";
  }
}
function mobile_menu() {
  var mobile = document.getElementById("nav_mobile_menu");
  if (mobile.style.display == "none") {
    mobile.style.display = "block";
  } else {
    mobile.style.display = "none";
  }
}
/* JS FOR  */
