<template>
    <div>
        <el-card shadow="hover" class="box-card">
            <el-main>
                <el-row :gutter="10">
                    {% for column in table.columns %}{% if not loop.first and column.column_name not in ignoreGenerateTheseColumnsInVue %}<el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" class="search-item">
                        <label class="search-title">{{ column.verbose_name }}</label>
                        {% if column.origin_type == 'date' or column.column_name == 'opdate' %}<el-date-picker
                            v-model="query{{ table.class_name }}Params.{{ column.column_name }}"
                            type="date"
                            format="yyyyMMdd"
                            value-format="yyyyMMdd"
                            placeholder="选择{{ column.verbose_name }}"
                        ></el-date-picker>
                        {% elif column.origin_type in ['int','bigint','decimal','float'] %}<el-input
                            v-model="query{{ table.class_name }}Params.{{ column.column_name }}"
                            type="number"
                            placeholder="请输入{{ column.verbose_name }}"
                            prefix-icon="el-icon-search"
                            clearable
                        ></el-input>
                        {% else %}<el-input
                            placeholder="请输入{{ column.verbose_name }}"
                            prefix-icon="el-icon-search"
                            v-model="query{{ table.class_name }}Params.{{ column.column_name }}"
                            maxlength="{{ column.max_length }}"
                            show-word-limit
                            clearable
                        ></el-input>{% endif %}
                    </el-col>{% endif %}{% endfor %}
                    <el-button
                            icon="el-icon-search"
                            circle
                            title="搜索"
                            @click="get{{ table.class_name }}List"
                            class="search-button"
                    ></el-button>
                    <el-button
                            icon="el-icon-plus"
                            circle
                            title="添加"
                            @click="add{{ table.class_name }}"
                            class="search-button"
                    ></el-button>
                </el-row>
            </el-main>
        </el-card>
        <el-divider></el-divider>
        <el-card shadow="hover" class="box-card">
            <el-table
                    :data="{{ table.title_name }}ListData"
                    border
                    style="width: 100%"
                    @sort-change="sortChange"
            >
                {% for column in table.columns %}{% if column.column_name not in ignoreGenerateTheseColumnsInVue %}<el-table-column
                        prop="{{ column.column_name }}"
                        label="{{ column.verbose_name }}"
                        sortable{% if loop.first %}fixed{% endif %}
                ></el-table-column>
                {% else %}<el-table-column
                    prop="{{ column.column_name }}"
                    label="{{ column.verbose_name }}"
                >
                <template slot-scope="scope">{{ '{{' }} scope.row.{{ column.column_name }} | timestampToDate {{ '}}' }}</template>
                </el-table-column>{% endif %}{% endfor %}
                <el-table-column label="操作" fixed="right" fit="true" width="130">
                    <template slot-scope="scope">
                        <el-button
                                type="primary"
                                icon="el-icon-edit"
                                circle
                                :title="scope.row.{{ table.columns[0].column_name }}"
                                @click="editThis{{ table.class_name }}(scope.row.{{ table.columns[0].column_name }})"
                                class="table-button"
                        ></el-button>
                        <el-button
                                type="danger"
                                icon="el-icon-delete"
                                circle
                                slot="reference"
                                class="table-button"
                                @click="deleteThis{{ table.class_name }}(scope.row.{{ table.columns[0].column_name }})"
                        ></el-button>
                    </template>
                </el-table-column>
            </el-table>
            <el-pagination
                    @size-change="sizeChange"
                    @current-change="pageChange"
                    :current-page="currentPage"
                    :page-sizes="[10, 20, 50, 100]"
                    :page-size="pageSize"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="total"
            ></el-pagination>
        </el-card>
        <{{ table.class_name }}Item
                :title="dialogTitle"
                @setDialogVisible="setDialogVisible"
                :visible="dialogVisible"
                :{{ table.columns[0].column_name }}="current{{ table.columns[0].column_name }}"
                @reloadData="get{{ table.class_name }}List"
        ></{{ table.class_name }}Item>
    </div>
</template>

<style lang="scss">
    .search-item {
        border-radius: 4px;
        margin: 5px 0;
        display: flex;

        .search-title {
            font-size: 16px;
            width: 180px;
            line-height: 40px;
            text-align: right;
            margin-right: 10px;
        }
    }

    .search-button {
        margin: 5px;
    }

    .table-button {
        margin: 0 5px;
    }

    .cell {
        white-space: nowrap !important;
    }

    .el-pagination {
        margin: 8px 10px 0 0;
        text-align: right;
    }
</style>

<script>
    import {{ table.class_name }}Item from './{{ table.class_name }}Item.vue'

    export default {
        name: '{{ table.class_name }}List',
        components: {
            {{ table.class_name }}Item
        },
        data() {
            return {
                {{ table.title_name}}ListData: [],
                currentPage: 1,
                pageSize: 50,
                total: 0,
                query{{ table.class_name }}Params: {},
                dialogVisible: false,
                dialogTitle: '',
                current{{ table.columns[0].column_name }}: ''
            }
        },
        watch: {},
        created() {
            this.get{{ table.class_name }}List()
        },
        methods: {
            async get{{ table.class_name }}List() {
                let url =
                    '{{ path }}/{{ table.title_name }}/?p=' + this.currentPage + '&pagesize=' + this.pageSize
                for (const key in this.query{{ table.class_name }}Params) {
                    if (this.query{{ table.class_name }}Params[key] !== null && this.query{{ table.class_name }}Params[key] !== '') {
                        url += '&' + key + '=' + this.query{{ table.class_name }}Params[key]
                    }
                }
                await this.$axios.get(url).then(result => {
                    this.{{ table.title_name}}ListData = result.results
                    this.total = result.count
                })
            },
            sizeChange(size) {
                this.pageSize = size
                this.get{{ table.class_name }}List()
            },
            pageChange(page) {
                this.currentPage = page
                this.get{{ table.class_name }}List()
            },
            sortChange(sort) {
                // { column, prop, order }
                console.log(sort)
                this.query{{ table.class_name }}Params['ordering'] =
                    (sort.order !== 'ascending' ? '-' : '') + sort.prop
                this.get{{ table.class_name }}List()
            },
            setDialogVisible(visible) {
                this.dialogVisible = visible
            },
            add{{ table.class_name }}() {
                this.current{{ table.columns[0].column_name }} = ''
                this.dialogTitle = '新增'
                this.dialogVisible = true
            },
            editThis{{ table.class_name }}({{ table.columns[0].column_name }}) {
                this.current{{ table.columns[0].column_name }} = {{ table.columns[0].column_name }}
                this.dialogTitle = '编辑'
                this.dialogVisible = true
            },
            deleteThis{{ table.class_name }}({{ table.columns[0].column_name }}) {
                this.$confirm('真的要删除吗？', '提示', {
                    confirmButtonText: '删除',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.$axios
                        .delete('{{ path }}/{{ table.title_name }}/' + {{ table.columns[0].column_name }})
                        .then(result => {
                            this.get{{ table.class_name }}List()
                            this.$notify({
                                title: '成功',
                                message: '删除成功！',
                                type: 'success'
                            })
                        })
                        .catch(() => {
                            this.$notify.error({
                                title: '错误',
                                message: '删除失败！'
                            })
                        })
                })
            }
        }
    }
</script>
