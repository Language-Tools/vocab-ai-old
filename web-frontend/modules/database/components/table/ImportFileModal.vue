<template>
  <Modal
    :right-sidebar="!isTableCreation"
    :right-sidebar-scrollable="true"
    @show="reset()"
    @hide="stopPollIfRunning()"
  >
    <template #content>
      <h2 class="box__title">
        {{
          isTableCreation
            ? $t('importFileModal.title')
            : $t('importFileModal.additionalImportTitle', {
                table: table.name,
              })
        }}
      </h2>
      <TableForm
        ref="tableForm"
        :creation="isTableCreation"
        @submitted="submitted"
      >
        <div class="control">
          <label class="control__label">
            {{ $t('importFileModal.importLabel') }}
          </label>
          <div class="control__elements">
            <ul class="choice-items">
              <li v-if="isTableCreation">
                <a
                  class="choice-items__link"
                  :class="{ active: importer === '' }"
                  @click=";[(importer = ''), reset()]"
                >
                  <i class="choice-items__icon fas fa-clone"></i>
                  {{ $t('importFileModal.newTable') }}
                </a>
              </li>
              <li
                v-for="importerType in importerTypes"
                :key="importerType.type"
              >
                <a
                  class="choice-items__link"
                  :class="{ active: importer === importerType.type }"
                  @click=";[(importer = importerType.type), reset()]"
                >
                  <i
                    class="choice-items__icon fas"
                    :class="'fa-' + importerType.iconClass"
                  ></i>
                  {{ importerType.getName() }}
                </a>
              </li>
            </ul>
          </div>
        </div>
        <component
          :is="importerComponent"
          :disabled="importInProgress"
          @changed="reset()"
          @header="onHeader($event)"
        />
        <Error :error="error"></Error>
        <Alert
          v-if="errorReport.length > 0 && error.visible"
          :title="$t('importFileModal.reportTitleFailure')"
          type="warning"
          icon="exclamation"
        >
          {{ $t('importFileModal.reportMessage') }} {{ errorReport.join(', ') }}
        </Alert>
        <Alert
          v-if="errorReport.length > 0 && !error.visible"
          :title="$t('importFileModal.reportTitleSuccess')"
          type="warning"
          icon="exclamation"
        >
          {{ $t('importFileModal.reportMessage') }} {{ errorReport.join(', ') }}
        </Alert>
        <div
          v-if="!jobHasSucceeded || errorReport.length === 0"
          class="modal-progress__actions"
        >
          <ProgressBar
            v-if="importInProgress && showProgressBar"
            :value="progressPercentage"
            :status="humanReadableState"
          />
          <div class="align-right">
            <button
              class="button button--large"
              :class="{
                'button--loading':
                  importInProgress || (jobHasSucceeded && !isTableCreated),
              }"
              :disabled="
                importInProgress ||
                !canBeSubmitted ||
                (jobHasSucceeded && !isTableCreated)
              "
            >
              {{
                isTableCreation
                  ? $t('importFileModal.addButton')
                  : $t('importFileModal.importButton')
              }}
            </button>
          </div>
        </div>
        <div v-else class="align-right">
          <button
            class="button button--large button--success"
            :class="{ 'button--loading': !isTableCreated }"
            @click.prevent="openTable"
          >
            {{
              isTableCreation
                ? $t('importFileModal.openCreatedTable')
                : $t('importFileModal.showTable')
            }}
          </button>
        </div>
      </TableForm>
    </template>
    <template v-if="!isTableCreation" #sidebar>
      <div class="field-mapping">
        <div v-if="header.length > 0" class="field-mapping__body">
          <h3>{{ $t('importFileModal.fieldMappingTitle') }}</h3>
          <p>{{ $t('importFileModal.fieldMappingDescription') }}</p>
          <div v-for="(head, index) in header" :key="head" class="control">
            <label class="control__label control__label--small">
              {{ head }}
            </label>
            <Dropdown v-model="mapping[index]">
              <DropdownItem name="Skip" :value="0" icon="ban" />
              <DropdownItem
                v-for="field in availableFields"
                :key="field.id"
                :name="field.name"
                :value="field.id"
                :icon="field._.type.iconClass"
                :disabled="
                  selectedFields.includes(field.id) &&
                  field.id !== mapping[index]
                "
              />
            </Dropdown>
          </div>
        </div>
        <div v-else class="field-mapping__empty">
          <i class="field-mapping__empty-icon fas fa-random" />
          <div class="field-mapping__empty-text">
            {{ $t('importFileModal.selectImportMessage') }}
          </div>
        </div>
      </div>
    </template>
  </Modal>
</template>

<script>
import { clone } from '@baserow/modules/core/utils/object'
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'
import jobProgress from '@baserow/modules/core/mixins/jobProgress'
import TableService from '@baserow/modules/database/services/table'
import _ from 'lodash'

import { ResponseErrorMessage } from '@baserow/modules/core/plugins/clientHandler'

import TableForm from './TableForm'

export default {
  name: 'ImportFileModal',
  components: { TableForm },
  mixins: [modal, error, jobProgress],
  props: {
    database: {
      type: Object,
      required: true,
    },
    table: {
      type: Object,
      required: false,
      default: null,
    },
    fields: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  data() {
    return {
      importer: '',
      uploadProgressPercentage: 0,
      importState: null,
      showProgressBar: false,
      header: [],
      mapping: {},
    }
  },
  computed: {
    isTableCreation() {
      return this.table === null
    },
    isTableCreated() {
      if (!this.job?.table_id) {
        return false
      }
      return this.database.tables.some(({ id }) => id === this.job.table_id)
    },
    canBeSubmitted() {
      return (
        this.isTableCreation ||
        (this.importer &&
          Object.values(this.mapping).some(
            (value) => this.fieldIndexMap[value] !== undefined
          ))
      )
    },
    fieldTypes() {
      return this.$registry.getAll('field')
    },
    /**
     * Map beetween the field id and his index in the array.
     */
    fieldIndexMap() {
      return Object.fromEntries(
        this.writableFields.map((field, index) => [field.id, index])
      )
    },
    /**
     * All writable fields.
     */
    writableFields() {
      return this.fields.filter(
        ({ type }) => !this.fieldTypes[type].getIsReadOnly()
      )
    },
    /**
     * All writable fields that can be imported into
     */
    availableFields() {
      return this.writableFields.filter(({ type }) =>
        this.fieldTypes[type].getCanImport()
      )
    },
    /**
     * Fields that are mapped to a column
     */
    selectedFields() {
      return Object.values(this.mapping)
    },
    progressPercentage() {
      switch (this.state) {
        case null:
          return 0
        case 'preparingData':
          return 1
        case 'uploading':
          // 10% -> 50%
          return (this.uploadProgressPercentage / 100) * 40 + 10
        default:
          // 50% -> 100%
          return 50 + this.job.progress_percentage / 2
      }
    },
    state() {
      if (this.job === null) {
        return this.importState
      } else {
        return this.job.state
      }
    },
    importInProgress() {
      return this.state !== null && !this.jobIsFinished && !this.error.visible
    },
    importerTypes() {
      return this.$registry.getAll('importer')
    },
    importerComponent() {
      return this.importer === ''
        ? null
        : this.$registry.get('importer', this.importer).getFormComponent()
    },
    humanReadableState() {
      switch (this.state) {
        case null:
          return ''
        case 'preparingData':
          return this.$t('importFileModal.preparing')
        case 'uploading':
          if (this.uploadProgressPercentage === 100) {
            return this.$t('job.statePending')
          } else {
            return this.$t('importFileModal.uploading')
          }
        default:
          return this.jobHumanReadableState
      }
    },
    errorReport() {
      if (this.job && Object.keys(this.job.report.failing_rows).length > 0) {
        return Object.keys(this.job.report.failing_rows)
          .map((key) => parseInt(key, 10) + 1)
          .sort((a, b) => a - b)
      } else {
        return []
      }
    },
  },
  beforeDestroy() {
    this.stopPollIfRunning()
  },
  methods: {
    reset(full = true) {
      this.job = null
      this.uploadProgressPercentage = 0
      if (full) {
        this.header = []
        this.importState = null
        this.mapping = {}
      }
      this.hideError()
    },
    onHeader(header) {
      this.header = header
      this.mapping = Object.fromEntries(
        header.map((name, index) => {
          const foundField = this.availableFields.find(
            ({ name: fieldName }) => fieldName === name
          )
          return [index, foundField ? foundField.id : 0]
        })
      )
    },
    /**
     * When the form is submitted we try to extract the initial data and first row
     * header setting from the values. An importer could have added those, but they
     * need to be removed from the values.
     */
    async submitted(formValues) {
      this.showProgressBar = false
      this.reset(false)
      let data = null
      const values = { ...formValues }

      if (
        Object.prototype.hasOwnProperty.call(values, 'getData') &&
        typeof values.getData === 'function'
      ) {
        try {
          this.showProgressBar = true
          this.importState = 'preparingData'
          await this.$ensureRender()

          data = await values.getData()

          if (!this.isTableCreation) {
            const fieldMapping = Object.entries(this.mapping)
              .filter(
                ([, targetFieldId]) =>
                  !!targetFieldId ||
                  // Check if we have an id from a removed field
                  this.fieldIndexMap[targetFieldId] !== undefined
              )
              .map(([importIndex, targetFieldId]) => {
                return [importIndex, this.fieldIndexMap[targetFieldId]]
              })

            // Template row with default values
            const defaultRow = this.writableFields.map((field) =>
              this.fieldTypes[field.type].getEmptyValue(field)
            )

            // Precompute the prepare value function for each field
            const prepareValueByField = this.writableFields.map(
              (field) => (value) =>
                this.fieldTypes[field.type].prepareValueForUpdate(
                  field,
                  this.fieldTypes[field.type].prepareValueForPaste(field, value)
                )
            )

            // Processes the data by chunk to avoid UI freezes
            const result = []
            for (const chunk of _.chunk(data, 1000)) {
              result.push(
                chunk.map((row) => {
                  const newRow = clone(defaultRow)
                  fieldMapping.forEach(([importIndex, targetIndex]) => {
                    newRow[targetIndex] = prepareValueByField[targetIndex](
                      row[importIndex]
                    )
                  })
                  return newRow
                })
              )
              await this.$ensureRender()
            }
            data = result.flat()
          } else {
            // Add the header in case of table creation
            data = [this.header, ...data]
          }

          delete values.header
        } catch (error) {
          this.reset()
          this.handleError(error, 'application')
        }
      }

      this.importState = 'uploading'

      const onUploadProgress = ({ loaded, total }) =>
        (this.uploadProgressPercentage = (loaded / total) * 100)

      try {
        if (data && data.length > 0) {
          this.showProgressBar = true
        }

        if (this.isTableCreation) {
          const { data: job } = await TableService(this.$client).create(
            this.database.id,
            values,
            data,
            true,
            {
              onUploadProgress,
            }
          )
          this.startJobPoller(job)
        } else {
          const { data: job } = await TableService(this.$client).importData(
            this.table.id,
            data,
            {
              onUploadProgress,
            }
          )
          this.startJobPoller(job)
        }
      } catch (error) {
        this.stopPollAndHandleError(error, {
          ERROR_MAX_JOB_COUNT_EXCEEDED: new ResponseErrorMessage(
            this.$t('job.errorJobAlreadyRunningTitle'),
            this.$t('job.errorJobAlreadyRunningDescription')
          ),
        })
      }
    },
    getCustomHumanReadableJobState(jobState) {
      const translations = {
        'row-import-creation': this.$t('importFileModal.stateRowCreation'),
        'row-import-validation': this.$t('importFileModal.statePreValidation'),
        'import-create-table': this.$t('importFileModal.stateCreateTable'),
      }
      return translations[jobState]
    },
    openTable() {
      // Redirect to the newly created table.
      this.$nuxt.$router.push({
        name: 'database-table',
        params: {
          databaseId: this.database.id,
          tableId: this.job.table_id,
        },
      })
      this.hide()
    },
    async onJobDone() {
      if (this.isTableCreation) {
        // Let's add the table to the store...
        const { data: table } = await TableService(this.$client).get(
          this.job.table_id
        )

        await this.$store.dispatch('table/forceCreate', {
          database: this.database,
          data: table,
        })
      } else {
        this.$bus.$emit('table-refresh', {
          tableId: this.job.table_id,
        })
      }
      if (this.errorReport.length === 0) {
        this.openTable()
      }
    },
    onJobFailed() {
      const error = new ResponseErrorMessage(
        this.$t('importFileModal.importError'),
        this.job.human_readable_error
      )
      this.stopPollAndHandleError(error)
    },
    onJobPollingError(error) {
      this.stopPollAndHandleError(error)
    },
    stopPollAndHandleError(error, specificErrorMap = null) {
      this.stopPollIfRunning()
      error.handler
        ? this.handleError(error, 'application', specificErrorMap)
        : this.showError(error)
    },
  },
}
</script>
