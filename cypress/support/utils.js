
cy.forms = {
    checkSummaryTableContent: (table, element, index, heading, value, editLabel) => {
        table
            .get(element)
            .eq(index)
            .within(() => {
                cy.contains(heading)
                cy.contains(value)

                if (editLabel) {
                    cy.get('a').contains(editLabel)
                }
            })
    }
}

export function urlBuilder(supplyChain, strategicAction, strategicActionUpdate) {

    let urls = {
        home: Cypress.config('baseUrl'),
        privacy: `${Cypress.config('baseUrl')}/privacy-notice/`,
        summary: `${Cypress.config('baseUrl')}/summary/`,
    }

    if (supplyChain) {
        urls.supplyChain = {
            taskList: `${Cypress.config('baseUrl')}/${supplyChain.fields.slug}/`,
        }

        if (strategicAction) {
            urls.supplyChain.strategicActions = {
                summary: `${Cypress.config('baseUrl')}/${supplyChain.fields.slug}/strategic-actions/`,
            }

            if (strategicActionUpdate) {
                urls.supplyChain.strategicActions.update = {
                    info: `${Cypress.config('baseUrl')}/${supplyChain.fields.slug}/${strategicAction.fields.slug}/updates/${strategicActionUpdate.fields.slug}/info/`,
                    timing: `${Cypress.config('baseUrl')}/${supplyChain.fields.slug}/${strategicAction.fields.slug}/updates/${strategicActionUpdate.fields.slug}/timing/`,
                    status: `${Cypress.config('baseUrl')}/${supplyChain.fields.slug}/${strategicAction.fields.slug}/updates/${strategicActionUpdate.fields.slug}/delivery-status/`,
                    revisedTiming: `${Cypress.config('baseUrl')}/${supplyChain.fields.slug}/${strategicAction.fields.slug}/updates/${strategicActionUpdate.fields.slug}/revised-timing/`,
                    confirm: `${Cypress.config('baseUrl')}/${supplyChain.fields.slug}/${strategicAction.fields.slug}/updates/${strategicActionUpdate.fields.slug}/confirm/`,
                    review: `/${supplyChain.fields.slug}/${strategicAction.fields.slug}/updates/${strategicActionUpdate.fields.slug}/review/`,
                }
            }
        }
    }


    return urls;
}
