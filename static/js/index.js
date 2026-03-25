$(document).ready(function () {
  $("#search-date-tab").hide();
  $("#date-search-form").submit(function (event) {
    event.preventDefault();
    $.get(
      "/contrevenants?du=" +
        $("#from_date").val() +
        "&au=" +
        $("#to_date").val(),
      function (data, status) {
        let listeContravention = [];
        console.log(status);
        data.forEach((contra) => {
          const element = listeContravention.find(
            (item) => item.business_id === contra.business_id,
          );
          if (element) {
            element.quantite += 1;
          } else {
            listeContravention.push({
              nom: contra.etablissement,
              business_id: contra.business_id,
              quantite: 1,
            });
          }
        });
        const $tbody = $("#contravention-table-body");
        $tbody.empty();
        listeContravention.forEach((contra) => {
          $tbody.append(`
                <tr class="align-top text-sm text-slate-700 transition hover:bg-slate-50/80">
                    <td class="px-4 py-4 text-slate-600">
                        <a href="/entreprise/${contra.business_id}">
                            ${contra.nom}
                        </a>                     
                    </td>
                    <td class="px-4 py-4 text-slate-600">${contra.quantite}</td>
                </tr>
           `);
        });
      },
    );
  });
});
