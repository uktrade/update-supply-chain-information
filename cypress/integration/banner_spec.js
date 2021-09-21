
import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'

const user = users[0].fields
const govDepartment = govDepartments[0].fields


describe('The banner', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrl'))
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y()
  })
  it("displays service name, user's name and department in header", () => {
    cy.get('div.service-banner-grid div a.govuk-header__link').contains('UK supply chain resilience tool')
    cy.get('div.service-banner-grid div .app-header-item').should(
      'have.text',
      `${user.first_name} ${user.last_name} - ${govDepartment.name}`
    )
  })
  it('Displays navigation links', () => {
    const navLinkNames = ['Home', 'Monthly update', 'Strategic action progress', 'Supply chain details']
    const navLinks = ['/', '/supply-chains/', '/action-progress/', '/chain-details/']

    cy.get('nav ul li.govuk-header__navigation-item')
      .should('have.length', 4)
      .each(($el, index) => {
        if (index == 0) {
          cy.wrap($el).get('li.govuk-header__navigation-item--active').should('exist')
          cy.wrap($el).find('a.govuk-header__link')
            .should('exist')
            .contains(navLinkNames[index])
            .should('have.attr', 'href')
            .and('equal', navLinks[index])
        } else {
          cy.wrap($el).find('li.govuk-header__navigation-item--active').should('not.exist')
          cy.wrap($el).find('a.govuk-header__link')
            .should('exist')
            .contains(navLinkNames[index])
            .should('have.attr', 'href')
            .and('equal', navLinks[index])
        }
      })
  })
})
