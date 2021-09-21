import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import { urlBuilder } from "../support/utils.js"

const adminUser = users[0].fields
const govDepartment = govDepartments[0].fields
const otherDept = govDepartments[1].fields
const supplyChain = supplyChains[0]
const urls = urlBuilder(supplyChain);


describe('The SCD filters page for admin user', () => {
  it('successfully loads', () => {
    cy.visit(urls.scd)
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y()
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${adminUser.first_name} ${adminUser.last_name} - ${govDepartment.name}`
    )
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Supply chain details`)
    cy.get('p').contains(`Filter supply chains by department`)
  })
  it('displays drop down for department', () => {
    cy.get('div > label').contains('Department')
    cy.get('div > label').find('Supply chain').should('not.exist')
    cy.get('div > select').should('have.length', 1)
  })
  it('displays enabled filter buttons', () => {
    cy.get('button').contains('Apply filters').should('be.enabled')
    cy.get('a').contains('Remove filters')
  })
  it('can select department', () => {
    cy.get('div > #id_department').select(`${govDepartment.name}`)
    cy.url().should('not.eq', urls.scd + `${govDepartment.name}/`)
  })
  it('can change department and bring back', () => {
    cy.get('div > #id_department').select(`${otherDept.name}`)
    cy.get('div > #id_department').select(`${govDepartment.name}`)
    cy.url().should('not.eq', urls.scd + `${govDepartment.name}/`)
  })
  it('can apply filter', () => {
    const successUrl = urls.scd + `${govDepartment.name}/`
    cy.get('div > #id_department').select(`${govDepartment.name}`)
    cy.url().should('not.eq', successUrl)
    cy.get('button').contains('Apply filters').click()
    cy.url().should('eq', successUrl)
  })
  it('can reset filters', () => {
    cy.get('a').contains('Remove filters').click()
    cy.url().should('eq', urls.scd)
  })
})

describe('Error handling of scd filter page', () => {
  it('successfully loads', () => {
    cy.visit(urls.scd)
  })
  it('trigger error by empty form submittion', () => {
    cy.get('button').contains('Apply filters').click()
    cy.url().should('eq', urls.scd)
    cy.get('#error-summary-title').contains('There is a problem')
    cy.get('li')
      .find('a')
      .contains('You must select a department to continue')
      .should('have.attr', 'href')
      .and('equal', '#id_department')
  })
})

