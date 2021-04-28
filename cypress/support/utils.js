
cy.forms = {
    checkSummaryTableContent: (table, element, index, heading, value, editLabel) => {
        table
          .get(element)
          .eq(index)
          .within(() => {
            cy.contains(heading)
            cy.contains(value)
            cy.get('a').contains(editLabel)
          })
      }
}
