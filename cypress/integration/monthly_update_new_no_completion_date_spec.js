import strategicActions from '../fixtures/strategicActions.json'
import strategicActionUpdates from '../fixtures/strategicActionUpdate.json'

const lastMonthUpdate = strategicActionUpdates.find((update) => {
  return /submitted last month/.test(update.fields.content);
});

const strategicActionPK = lastMonthUpdate.fields.strategic_action;

const strategicAction = strategicActions.find((action) => {
  return action.pk === strategicActionPK;
}).fields;

Cypress.Cookies.debug(true);

describe('Starting a new Monthly Update for a Strategic Action with no completion date', () => {
  beforeEach(() => {
    Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
  })
  it('successfully loads', () => {
    cy.visit(`http://localhost:8001/strategic-actions/${strategicActionPK}/update/start/`)
  })
  context('The page', () => {
    it('has no accessibility issues', () => {
      cy.runA11y()
    })
    it('displays the correct page header', () => {
      cy.get('h1').contains(
          'Strategic action monthly update'
      )
    })
    it('displays the previous update', () => {
      cy.get('h2:first').contains('Last update')
      cy.get('h2:first + p').contains('submitted last month')
    })
  })
  context('The Info form page', () => {
    beforeEach(() => {
      cy.get('main form').as('theForm')
    })
    it('should exist', () => {
      cy.get("@theForm").should('exist')
    })
    it('should have a CSRF token', () => {
      cy.get("@theForm").get('input[type="hidden"][name="csrfmiddlewaretoken"]').should('exist').invoke('val')
    })
    it('the CSRF token must not be empty', () => {
      cy.get("@theForm").get('input[type="hidden"][name="csrfmiddlewaretoken"]').invoke('val').should('not.be.empty')
    })
    it ('should have a textarea for the "content" field', () => {
      cy.get("@theForm").within((theForm) => {
        cy.get('textarea[name="content"]').should('exist')
      })
    })
    it('should have a submit button saying "Save and continue"', () => {
      cy.get('@theForm').within((theForm) => {
        cy.get('button[type="submit"]').should('exist')
        cy.get('button[type="submit"]').contains('Save and continue')
      })
    })
    it ('should go to the "Timing" page when saved', () => {
      cy.get('@theForm').within((theForm) => {
        cy.location('pathname').invoke('split', '/').its(4).as('strategicActionUpdateID')
        cy.get('@strategicActionUpdateID').then(strategicActionUpdateID => {
          cy.get('button[type="submit"]').click()
          cy.url().should('eq', `http://localhost:8001/strategic-actions/fd317f3e-9ce0-4ed0-9a6a-baf7c6e65989/update/${strategicActionUpdateID}/timing/`)
        })
      })
    })
  })
})
