import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import strategicActions from '../fixtures/strategicActions.json'
import { urlBuilder } from "../support/utils.js"

const user = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[0]
const stratAction = strategicActions[2]

const urls = urlBuilder(supplyChain, stratAction);

describe('The Strategicaction edit page', () => {
  it('successfully loads', () => {
    cy.visit(urls.supplyChain.strategicAction.edit)
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y('html', {
      rules: {
        "aria-allowed-attr": { enabled: false }
      }
    })
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${user.first_name} ${user.last_name} - ${govDepartment.name}`
    )
  })
  it('displays breadcrumbs', () => {
    cy.get('ol').children().should('have.length', 3)
    cy.get('li').contains('Home').should('have.attr', 'href').and('eq', '/')
    cy.get('li')
      .contains('Strategic action summary')
      .should('have.attr', 'href')
      .and('match', /.*#/)
    cy.get('li')
      .contains(`Strategic actions for ${supplyChain.fields.name}`)
      .should('have.attr', 'href')
      .and('eq', urls.supplyChain.strategicActions.summary.substring(21))
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Update ${stratAction.fields.name}`)
  })
  it('should have a CSRF token', () => {
    cy.mainForm().hasDjangoCSRFToken()
  })
  it('To enter description for SA', () => {
    cy.get('#description-field').children('textarea').type('Hello World')
  })
  it('To enter description for SA', () => {
    cy.get('#impact-field').children('textarea').type('Minor')
  })
  it('To select SAs category', () => {
    cy.get('#category-field').get('fieldset.govuk-fieldset > .govuk-radios').should('have.length', 4)
    cy.get('#category-field').get('fieldset.govuk-fieldset > .govuk-radios > .govuk-radios__item > input[type="radio"]').first().check()
  })
  it('To select SAs geographic scope', () => {
    cy.get('#scope-field > fieldset.govuk-fieldset > .govuk-radios > .govuk-radios__item').should('have.length', 2)
    cy.get('#scope-field > fieldset.govuk-fieldset > .govuk-radios > .govuk-radios__item > input[type="radio"]').first().check()
  })
  it('To set SA as on going', () => {
    cy.get('#on-going-field > fieldset.govuk-fieldset > .govuk-radios > .govuk-radios__item').should('have.length', 2)
    cy.get('#on-going-field > fieldset.govuk-fieldset > .govuk-radios > .govuk-radios__item > input[type="radio"]').last().check()
  })
  it('To set whole supply chain dependency', () => {
    cy.get('#related-field > fieldset.govuk-fieldset > .govuk-radios > .govuk-radios__item > input[type="radio"]').should('have.length', 2)
    cy.get('#related-field > fieldset.govuk-fieldset > .govuk-radios > .govuk-radios__item > input[type="radio"]').first().check()
  })
  it('To select supporting orgs', () => {
    cy.get('#sup-orgs-field > fieldset.govuk-fieldset > .govuk-checkboxes > .govuk-checkboxes__item').should('have.length', 12)
    cy.get('[type="checkbox"]').check()
  })
  it('To enter other dependencies', () => {
    cy.get('#other-deps-field').children('textarea').type('multiple dependencies')
  })
  it('displays the correct link back to summary', () => {
    cy.get('.govuk-button-group > a').contains('Cancel').should('have.attr', 'href').and('equal', urls.supplyChain.strategicActions.summary.substring(21))
  })
  it('To be able to save changes', () => {
    cy.get('.govuk-button-group > .govuk-button').contains('Save update').click()
    cy.url().should('eq', urls.supplyChain.strategicActions.summary)
  })
})


describe('SA Edit page with nested forms', () => {
  it('successfully loads', () => {
    cy.visit(urls.supplyChain.strategicAction.edit)
  })
  it('Display completion date', () => {
    cy.get('#on-going-field > fieldset.govuk-fieldset > .govuk-radios > .govuk-radios__item > input[type="radio"]').first().as('estimatedDate')
    cy.get('@estimatedDate').check()

    cy.get('@estimatedDate')
      .revealedElement()
      .should('be.visible')

    cy.get('@estimatedDate')
      .revealedElement().as('dateField')

    cy.get('@dateField').within(() => {
      cy.get('input').eq(0).invoke('attr', 'id').then((fieldID) => {
        cy.get('input').eq(0).should('have.attr', 'name', 'False-target_completion_date_day')
        cy.get(`label[for="${fieldID}"]`).should('exist').contains('Day').should('exist')
        cy.get('input').eq(0).clear()
        cy.get('input').eq(0).type('31')
      })
      cy.get('input').eq(1).invoke('attr', 'id').then((fieldID) => {
        cy.get('input').eq(1).should('have.attr', 'name', 'False-target_completion_date_month')
        cy.get(`label[for="${fieldID}"]`).should('exist').contains('Month').should('exist')
        cy.get('input').eq(1).clear()
        cy.get('input').eq(1).type('12')
      })
      cy.get('input').eq(2).invoke('attr', 'id').then((fieldID) => {
        cy.get('input').eq(2).should('have.attr', 'name', 'False-target_completion_date_year')
        cy.get(`label[for="${fieldID}"]`).should('exist').contains('Year').should('exist')
        cy.get('input').eq(2).clear()
        cy.get('input').eq(2).type('2022')
      })
    })
  })
  it('Display relational widget', () => {
    cy.get('#related-field > fieldset.govuk-fieldset > .govuk-radios > .govuk-radios__item > input[type="radio"]').last().as('partialRelation')
    cy.get('@partialRelation').check()
    cy.get('@partialRelation')
      .revealedElement()
      .should('be.visible')
    cy.get('@partialRelation').revealedElement().children(0).children('textarea').type('Partially affected')
  })
  it('To be able to save changes', () => {
    cy.get('.govuk-button-group > .govuk-button').contains('Save update').click()
    cy.url().should('eq', urls.supplyChain.strategicActions.summary)
  })
})
