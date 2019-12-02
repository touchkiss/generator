<template>
    <el-dialog :title="title" :visible.sync="dialogVisible">
        <el-form
                ref="{{ table.title_name }}Form"
                :model="{{ table.title_name }}Form"
                :rules="rules"
                label-width="100px"
                >
            <el-main>
                {% for column in table.columns %}{% if not loop.first %}<el-row :gutter="10">
                    <el-col :xs="24" :sm="24" :md="24" :lg="18" :xl="18">
                        <el-form-item label="{{ column.verbose_name }}" prop="{{ column.column_name }}">
                            {% if column.origin_type == 'date' or column.column_name == 'opdate' %}<el-date-picker
                                v-model="{{ table.title_name }}Form.{{ column.column_name }}"
                                type="date"
                                format="yyyyMMdd"
                                value-format="yyyyMMdd"
                                placeholder="选择{{ column.verbose_name }}"
                                ></el-date-picker>
                            {% elif column.origin_type in ['int','bigint','decimal','float'] %}<el-input
                                v-model="{{ table.title_name }}Form.{{ column.column_name }}"
                                    type="number"
                                    placeholder="请输入{{ column.verbose_name }}"
                                    clearable
                                ></el-input>
                            {% else %}<el-input
                                v-model="{{ table.title_name }}Form.{{ column.column_name }}"
                                type="text"
                                placeholder="请输入{{ column.verbose_name }}"
                                maxlength="{{ column.max_length }}"
                                show-word-limit
                                clearable
                                ></el-input>
                        {% endif %}</el-form-item>
                    </el-col>
                </el-row>{% endif %}{% endfor %}
            </el-main>
            <el-form-item>
                <el-button type="primary" @click="submitForm()">保存</el-button>
                <el-button type="danger" @click="resetForm()">重置</el-button>
                <el-button @click="dialogVisible=false">取消</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<style lang="scss">
    .el-form-item__label {
        font-size: 16px;
        width: 150px !important;
        line-height: 40px;
        text-align: right;
    }
    .el-form-item {
        .el-form-item__content {
            margin-left: 150px !important;
        }
        .el-input{
            min-width: 220px;
        }
    }
</style>

<script>
    export default {
        props: ['visible', 'title', '{{ table.columns[0].column_name }}'],
        data() {
            return {
                dialogVisible: this.visible,
                {{ table.title_name }}Form: {{ '{' }}{% for column in table.columns %}{% if not loop.first %}   {{ column.column_name }}: ''{{ ',' if not loop.last }}{% endif %}
                {% endfor %}},
                rules: {{ '{' }}{% for column in table.columns %}{% if not loop.first %}    {{ column.column_name }}: [
                        { required: {{ 'true' if column.nullable=='NO' else 'false'}}, message: '请输入{{ column.verbose_name }}', trigger: 'blur' }
                    ]{{ ',' if not loop.last }}{% endif %}
                {% endfor %}}
            }
        },
        watch: {
            {{ table.columns[0].column_name }}() {
                this.init()
            },
            visible() {
                this.dialogVisible = this.visible
            },
            dialogVisible() {
                this.$emit('setDialogVisible', this.dialogVisible)
                this.init()
            }
        },
        methods: {
            init() {
                if (this.{{ table.columns[0].column_name }} != null && this.{{ table.columns[0].column_name }} !== '') {
                    this.$axios.get('{{ path }}/{{ table.title_name }}/' + this.{{ table.columns[0].column_name }} + '/').then(result => {
                        this.{{ table.title_name }}Form = result
                    })
                } else {
                    this.resetForm()
                    delete this.{{ table.title_name }}Form['{{ table.columns[0].column_name }}']
                }
            },
            submitForm() {
                this.$refs['{{ table.title_name }}Form'].validate(valid => {
                    if (valid) {
                        if (this.{{ table.columns[0].column_name }} != null && this.{{ table.columns[0].column_name }} !== '') {
                            this.{{ table.title_name }}Form.{{ table.columns[0].column_name }} = this.{{ table.columns[0].column_name }}
                            this.$axios
                                .put('{{ path }}/{{ table.title_name }}/' + this.{{ table.columns[0].column_name }} + '/', this.{{ table.title_name }}Form)
                                .then(result => {
                                    this.saveSuccessed()
                                })
                                .catch(error => {
                                    this.saveFailed(error)
                                })
                        } else {
                            this.$axios
                                .post('{{ path }}/{{ table.title_name }}/', this.{{ table.title_name }}Form)
                                .then(result => {
                                    this.saveSuccessed()
                                })
                                .catch(error => {
                                    this.saveFailed(error)
                                })
                        }
                    } else {
                        console.log('error submit!!')
                        return false
                    }
                })
            },
            resetForm() {
                this.$refs['{{ table.title_name }}Form'].resetFields()
            },
            saveSuccessed() {
                this.$emit('reloadData')
                this.$notify({
                    title: '成功',
                    message: '保存成功！',
                    type: 'success'
                })
                this.resetForm()
                this.dialogVisible = false
            },
            saveFailed(error) {
                console.log(error)
                this.$notify.error({
                    title: '错误',
                    message: '保存失败！'
                })
                this.resetForm()
                this.dialogVisible = false
            }
        }
    }
</script>
