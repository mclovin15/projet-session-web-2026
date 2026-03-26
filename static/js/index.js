function getStatusViolationColor(status) {
  const normalizedStatus = (status || "").toLowerCase();

  if (normalizedStatus === "fermé changement d'exploitant") {
    return "bg-yellow-100 text-yellow-800 border-yellow-200";
  } else if (normalizedStatus === "ouvert") {
    return "bg-green-100 text-green-800 border-green-200";
  } else if (normalizedStatus === "fermé") {
    return "bg-red-100 text-red-800 border-red-200";
  } else {
    return "bg-gray-100 text-gray-800 border-gray-200";
  }
}

$(document).ready(function () {
  $("#search-date-tab").hide();
  $("#search-resto-section").hide();
  $("#resto-error").hide();

  $("#clear-restaurant-select").on("click", function () {
    $("#restaurant-select").val("");
    $("#resto-error").hide().text("");
    $("#restaurant-select").focus();
  });

  $("#resto-search-form").on("submit", function (event) {
    event.preventDefault();

    const selectedValue = $("#restaurant-select").val().trim();
    const businessId = $("#restaurant-options option")
      .filter(function () {
        return $(this).val() === selectedValue;
      })
      .attr("data-business_id");

    if (!selectedValue || !businessId) {
      let $restoError = $("#resto-error");

      if (!$restoError.length) {
        $restoError = $(
          '<div id="resto-error" class="mt-4 text-sm font-medium text-red-600"></div>',
        );
        $("#resto-search-form").after($restoError);
      }

      $restoError.text("Veuillez sélectionner un restaurant dans la liste.");
      $restoError.show();
      return;
    }

    $("#resto-error").hide().text("");

    $.ajax({
      url: "/etablissement/" + businessId,
      method: "GET",
      dataType: "json",
      success: function (data, status) {
        const nom = data.nom;
        const adresse = data.adresse;
        const business_id = data.business_id;
        const ville = data.ville;
        const proprio = data.proprietaire;
        const categorie = data.categorie;
        const montantTotal = data.montantTotal;
        const nbViolations = data.nombre_violations;
        const listeViolations = data.violations;

        $("#resto-name").html(nom);
        $("#resto-adresse").html(adresse);
        $("#resto-bussiness_id").html(business_id);
        $("#resto-ville").html(ville);
        $("#resto-proprio").html(proprio);
        $("#resto-cat").html(categorie);
        $("#resto-montantTotal").html(montantTotal + " $");
        $("#resto-nb-infract").html(nbViolations);

        const $container = $("#resto-violations");
        console.log(listeViolations[0]);
        listeViolations.forEach((item) => {
          const statusClass = getStatusViolationColor(item.statut);
          // TODO: réduire la nb de ligne en splittant dans une fonction
          $container.append(`
    <article class="overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white shadow-soft">
      <div class="grid gap-6 px-6 py-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,0.9fr)]">
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <span class="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-600">
              Poursuite #${item.id_poursuite}
            </span>
            <span class="inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${statusClass}">
              ${item.statut}
            </span>
          </div>

          <p class="mt-4 text-base leading-7 text-slate-700">
            ${item.description}
          </p>
        </div>

        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
              Date de violation
            </p>
            <p class="mt-2 text-base font-semibold text-slate-900">
              ${item.date_violation}
            </p>
          </div>

          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
              Date de jugement
            </p>
            <p class="mt-2 text-base font-semibold text-slate-900">
              ${item.date_jugement}
            </p>
          </div>

          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
              Date du statut
            </p>
            <p class="mt-2 text-base font-semibold text-slate-900">
              ${item.date_statut}
            </p>
          </div>

          <div class="rounded-2xl bg-slate-900 p-4 text-white">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">
              Montant
            </p>
            <p class="mt-2 text-2xl font-black">
              ${item.montant} $
            </p>
          </div>
        </div>
      </div>
    </article>
  `);
        });

        if (listeViolations.length === 0) {
          $("#date-search-error").text("Aucune contravention trouvee.");
          return;
        }

        $("#search-resto-section").show();
      },
      error: function (xhr) {
        const errorMessage =
          xhr.responseJSON && xhr.responseJSON.error
            ? xhr.responseJSON.error
            : "Une erreur est survenue lors de la requete.";
        $("#resto-error").show();
        $("#resto-error").text(errorMessage);
      },
    });
  });

  $("#date-search-form").submit(function (event) {
    event.preventDefault();

    $("#date-search-error").text("");
    $("#contravention-table-body").empty();
    $("#search-date-tab").hide();

    $.ajax({
      url: "/contrevenants",
      method: "GET",
      data: {
        du: $("#from_date").val(),
        au: $("#to_date").val(),
      },
      dataType: "json",
      success: function (data, status) {
        let listeContravention = [];

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

        if (listeContravention.length === 0) {
          $("#date-search-error").text("Aucune contravention trouvee.");
          return;
        }

        $("#search-date-tab").show();
      },
      error: function (xhr) {
        const errorMessage =
          xhr.responseJSON && xhr.responseJSON.error
            ? xhr.responseJSON.error
            : "Une erreur est survenue lors de la requete.";

        $("#date-search-error").text(errorMessage);
      },
    });
  });
});
