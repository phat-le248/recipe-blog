editing = 0

function load_data(query)
{
 $.ajax({
  url:"/recipe/search",
  method:"POST",
  data:{query:query},
  success:function(data)
  {
    $('#search_result').html(data);
    $("#search_result").append(data.htmlresponse);
  }
 });
}

function add_recipe(recipe_name)
{
 if (editing != 0) {
   $.ajax({
    url:"/menu/create/add-recipe",
    method:"POST",
    data:{menu_idx:editing, recipe_name:recipe_name},
    success:function(data)
    {
      $('#day-menus').html(data);
      $("#day-menus").append(data.htmlresponse);
    }
   });
 }
};

function remove_recipe(recipe_name)
{
 if (editing != 0) {
   $.ajax({
    url:"/menu/create/remove-recipe",
    method:"POST",
    data:{menu_idx:editing, recipe_name:recipe_name},
    success:function(data)
    {
      $('#day-menus').html(data);
      $("#day-menus").append(data.htmlresponse);
    }
   });
  }
}

function add_menu()
{
 $.ajax({
  url:"/menu/create/add-menu",
  method:"POST",
  data:{},
  success:function(data)
  {
    $('#day-menus').html(data);
    $("#day-menus").append(data.htmlresponse);
  }
 });
}

function remove_menu(menu_idx)
{
 $.ajax({
  url:"/menu/create/remove-menu",
  method:"POST",
  data:{menu_idx:menu_idx},
  success:function(data)
  {
    $('#day-menus').html(data);
    $("#day-menus").append(data.htmlresponse);
  }
 });
}

function toggle_btn(menu_opts) {
  edit = !menu_opts.children[0].classList.contains("invisible-btn")
  if (edit) {
    reset_opts()
    editing = menu_opts.id
  }
  else {
    editing = 0
  }
  toggle_opt(menu_opts)
}

function reset_opts(opts){
  menu_opts = document.querySelectorAll(".day-menu-opts")
  remove_btns = document.querySelectorAll(".remove-recipe-btn")

  menu_opts.forEach((opts) => {
    opts.children[0].classList.remove("invisible-btn")
    opts.children[1].classList.add("invisible-btn")
  })

  remove_btns.forEach((btn) => {
    btn.classList.add("invisible-btn")
  })
}

function toggle_opt(opts){
  for (const btn of opts.children) {
    btn.classList.toggle("invisible-btn")
  }

  menu_id = `menu-${opts.id}`
  menu = document.getElementById(menu_id)
  menu_remove_btns = menu.querySelectorAll('.remove-recipe-btn')
  for (const btn of menu_remove_btns) {
    btn.classList.toggle("invisible-btn")
  }
}

// Events
$('#search_text').keyup(function(){
  var search = $(this).val();
  if(search != ''){
  load_data(search);
 }
});

const menu_add_btn = document.querySelector("#menu-add-btn")
$('#menu-add-btn').click(function(){
  add_menu()
})


