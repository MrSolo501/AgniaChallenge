
# TypeHints Definition
RepoName = Annotated[str, Field(description="Full name of the repository in the format 'owner/repo'")]
BranchName = Annotated[str, Field(description="Name of the branch in the repository")]
CommitSHA = Annotated[str, Field(description="SHA of the commit in the repository")]
FilePath = Annotated[str, Field(description="Path to the file in the repository")]
Message = Annotated[str, Field(description="Commit message for creating or updating a file")]
PullRequestTitle = Annotated[str, Field(description="Title for the pull request")]
PullRequestState = Annotated[Literal["open", "closed", "all"], Field(description="State of pull requests to list")]
PullRequestNumber = Annotated[int, Field(description="Number of the pull request")]
FileContent = Annotated[str, Field(description="Content to write to a file, encoded in base64")]

# Models Definition
class Branch(BaseModel):
    name: BranchName
    commit_sha: CommitSHA

class PullRequest(BaseModel):
    id: int
    title: PullRequestTitle
    state: PullRequestState
    number: PullRequestNumber
    created_at: datetime
    updated_at: datetime

class File(BaseModel):
    path: FilePath
    content: FileContent
    sha: str

# API Calls Documentation
## `star_repository`
**Description**: Stars a specified GitHub repository for the authenticated user.
- **Parameters**:
    - repo (RepoName): The repository to star.
- **Returns**: dict with a message indicating success or failure.

## `unstar_repository`
**Description**: Removes a star from a specified GitHub repository for the authenticated user.
- **Parameters**:
    - repo (RepoName): The repository to unstar.
- **Returns**: dict with a message indicating success or failure.

## `list_branches`
**Description**: Retrieves a list of branches in a specified GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository to list branches from.
- **Returns**: List of Branch objects.

## `create_branch`
**Description**: Creates a new branch in a GitHub repository from a given commit SHA.
- **Parameters**:
    - repo (RepoName): The repository to create the branch in.
    - branch_name (BranchName): Name of the new branch.
    - commit_sha (CommitSHA): SHA of the commit from which to create the branch.
- **Returns**: dict with details of the created branch.

## `delete_branch`
**Description**: Deletes a specified branch in a GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository where the branch exists.
    - branch_name (BranchName): The branch to delete.
- **Returns**: dict with a message indicating success or failure.

## `get_file_content`
**Description**: Retrieves the content of a specified file in a GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository to retrieve the file from.
    - file_path (FilePath): Path to the file in the repository.
    - branch (BranchName): Branch to get the file from (default is 'main').
- **Returns**: dict with decoded file content.

## `create_file`
**Description**: Creates a new file in a GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository to create the file in.
    - file_path (FilePath): Path where the file will be created.
    - content (FileContent): Base64-encoded content of the file.
    - branch (BranchName): Branch to create the file in.
    - message (Message): Commit message for file creation.
- **Returns**: dict with details of the created file.

## `update_file`
**Description**: Updates an existing file in a GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository containing the file.
    - file_path (FilePath): Path to the file.
    - content (FileContent): Base64-encoded new content of the file.
    - branch (BranchName): Branch to update the file in.
    - message (Message): Commit message for the update.
- **Returns**: dict with details of the updated file.

## `delete_file`
**Description**: Deletes a specified file from a GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository containing the file.
    - file_path (FilePath): Path to the file.
    - branch (BranchName): Branch from which to delete the file.
    - message (Message): Commit message for file deletion.
- **Returns**: dict with a message indicating success or failure.

## `create_pull_request`
**Description**: Creates a new pull request between specified branches in a GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository to create the pull request in.
    - title (PullRequestTitle): Title of the pull request.
    - head (BranchName): Source branch for the pull request.
    - base (BranchName): Target branch for the pull request.
    - body (Optional[str]): Description of the pull request.
- **Returns**: dict with details of the created pull request.

## `list_pull_requests`
**Description**: Retrieves a list of pull requests in a GitHub repository, optionally filtered by state.
- **Parameters**:
    - repo (RepoName): The repository to list pull requests from.
    - state (PullRequestState): State of pull requests to retrieve (default is 'open').
- **Returns**: List of PullRequest objects.

## `merge_pull_request`
**Description**: Merges a specified pull request in a GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository containing the pull request.
    - pull_number (PullRequestNumber): Number of the pull request.
    - commit_message (Message): Commit message for the merge.
- **Returns**: dict with details of the merge result.

## `close_pull_request`
**Description**: Closes a specified pull request in a GitHub repository without merging.
- **Parameters**:
    - repo (RepoName): The repository containing the pull request.
    - pull_number (PullRequestNumber): Number of the pull request.
- **Returns**: dict with details of the closed pull request.

## `create_issue`
**Description**: Creates a new issue in the specified GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository where the issue will be created.
    - title (IssueTitle): The title of the issue.
    - body (Optional[BodyContent]): Description of the issue.
    - labels (Optional[List[Label]]): List of labels to assign to the issue.
- **Returns**: dict with details of the created issue.

## `create_repository`
**Description**: Creates a new GitHub repository.
- **Parameters**:
    - name (str): The name of the repository.
    - description (Optional[str]): A short description of the repository.
    - private (bool): If true, the repository will be private.
- **Returns**: dict with details of the created repository.

## `delete_repository`
**Description**: Deletes a specified GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository to delete.
- **Returns**: dict with a message indicating success or failure.

## `get_issue`
**Description**: Retrieves details of a specific issue in a GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository containing the issue.
    - issue_number (int): The number of the issue to retrieve.
- **Returns**: dict with details of the issue.

## `update_issue`
**Description**: Updates an existing issue in a GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository containing the issue.
    - issue_number (int): The number of the issue to update.
    - title (Optional[IssueTitle]): New title for the issue.
    - body (Optional[BodyContent]): New content for the issue body.
- **Returns**: dict with details of the updated issue.

## `close_issue`
**Description**: Closes a specific issue in a GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository containing the issue.
    - issue_number (int): The number of the issue to close.
- **Returns**: dict with details of the closed issue.

## `list_issues`
**Description**: Retrieves a list of issues in a specified GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository to list issues from.
    - state (Literal["open", "closed", "all"]): Filter by issue state (default is 'open').
- **Returns**: List of issues in the repository.

## `get_repository_info`
**Description**: Retrieves information about a specific GitHub repository.
- **Parameters**:
    - repo (RepoName): The repository to retrieve information from.
- **Returns**: dict with details of the repository.
